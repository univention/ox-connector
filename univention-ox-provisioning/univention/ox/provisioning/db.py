# -*- coding: utf-8 -*-
#
# Copyright 2025 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.


import os
import logging
import json
from pathlib import Path
from itertools import chain
import datetime
from contextlib import contextmanager
from copy import deepcopy
from urllib.parse import urlsplit

import ldap.dn

from sqlalchemy import (
    create_engine,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Index,
)
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import inspect as sa_inspect

from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.soap.config import NoContextAdminPassword
from univention.ox.provisioning.helpers import get_obj_by_name_from_ox

Base = declarative_base()

# db_password = os.environ["DB_PASSWORD"]
# docker_host_name = os.environ["DOCKER_HOST_NAME"]
# engine = create_engine(f"postgresql+psycopg2://ox-connector:{db_password}@{docker_host_name}:5432/ox-connector")

LISTENER_DIR = Path(
    "/var/lib/univention-appcenter/apps/ox-connector/data/listener/",
)


def get_db_url():
    db_connection_string = os.environ.get(
        "OX_CONNECTOR_DB",
        str(LISTENER_DIR / "ox-connector.db"),
    )

    url = urlsplit(db_connection_string)
    if not url.scheme:
        return make_url(f"sqlite:///{db_connection_string}")

    return make_url(url.geturl())


DB_URL = get_db_url()
engine = create_engine(DB_URL)

User = get_ox_integration_class("SOAP", "User")
CACHE = {}
logger = logging.getLogger("listener")


class Relation(Base):
    __tablename__ = "relations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    src_obj_id = Column(
        String,
        ForeignKey("old.obj_id", ondelete="CASCADE"),
        nullable=False,
    )
    src_udm_module = Column(String, nullable=False)
    dst_obj_id = Column(
        String,
        ForeignKey("old.obj_id", ondelete="CASCADE"),
        nullable=False,
    )
    dst_udm_module = Column(String, nullable=False)
    relation_name = Column(String, nullable=False)

    __table_args__ = (
        Index("relations_lookup", "src_obj_id", "relation_name"),
        Index("relations_reverse_lookup", "dst_obj_id", "relation_name"),
    )

    def __str__(self):
        return f"Rel({self.src_udm_module}/{self.src_obj_id} -> {self.dst_udm_module}/{self.dst_obj_id}: {self.relation_name})"


class Dead(Base):
    __tablename__ = "morgue"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)
    error_msg = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (Index("morgue_obj_id", "obj_id"),)

    def __str__(self):
        return f"{self.dn} ({self.obj_id}; {self.udm_module}; {self.__tablename__}:{self.id})"


class Old(Base):
    __tablename__ = "old"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)
    forward_relations = relationship(
        "Relation",
        foreign_keys=[Relation.src_obj_id],
        cascade="delete",
    )  # only defined for cascade
    backward_relations = relationship(
        "Relation",
        foreign_keys=[Relation.dst_obj_id],
        cascade="delete",
    )  # only defined for cascade

    __table_args__ = (
        Index("old_obj_id", "obj_id"),
        Index("old_dn", "dn"),
    )

    def __str__(self):
        return f"{self.dn} ({self.obj_id}; {self.udm_module}; {self.__tablename__}:{self.id})"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)
    status = Column(String, nullable=False, default="new")
    num_errors = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (Index("tasks_created_at", "created_at"),)

    def __str__(self):
        return f"{self.dn} ({self.obj_id}; {self.udm_module}; {self.__tablename__}:{self.id})"


Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def add_relation(
    src_obj_id,
    src_udm_module,
    dst_obj_id,
    dst_udm_module,
    relation_name,
):
    """
    Add a Relation object
    """
    relation = Relation(
        src_obj_id=src_obj_id,
        src_udm_module=src_udm_module,
        dst_obj_id=dst_obj_id,
        dst_udm_module=dst_udm_module,
        relation_name=relation_name,
    )
    logger.info("Adding relation %s", relation)
    with _get_session() as db_session:
        db_session.add(relation)


def remove_complete_relation(src_obj_id, relation_name):
    """
    Remove all occurences of a relation name for an object
    """
    with _get_session() as db_session:
        for relation in (
            db_session.query(Relation)
            .filter_by(src_obj_id=src_obj_id, relation_name=relation_name)
            .all()
        ):
            logger.info("Deleting relation %s", relation)
            db_session.delete(relation)


def search_src_of_relation(dst_obj_id, relation_name):
    """
    Yield the src_obj_id of every relation pointing to dst_obj_id with the given relation_name.
    """
    with _get_session() as db_session:
        relations = (
            db_session.query(Relation)
            .filter_by(dst_obj_id=dst_obj_id, relation_name=relation_name)
            .all()
        )
        result = [r.src_obj_id for r in relations]
        for relation in relations:
            logger.info("Found relation %s", relation)
    yield from result


def get_task(obj_id: str = None):
    """
    Returns the first pending task with a given obj_id
    """
    if obj_id is None:
        return None
    with _get_session() as db_session:
        return db_session.query(Task).filter_by(obj_id=obj_id).first()


def get_tasks(udm_module: str = None, filter_empty_attributes: bool = None):
    """
    Return all tasks sorted by creation time.
    """
    with _get_session() as db_session:
        tasks = db_session.query(Task)
        if udm_module:
            tasks = tasks.filter_by(udm_module=udm_module)
        if filter_empty_attributes is True:
            tasks = tasks.filter(Task.attrs.is_(None))
        elif filter_empty_attributes is False:
            tasks = tasks.filter(Task.attrs.is_not(None))
        for task in tasks.order_by(Task.created_at):
            logger.debug("Yielding task %s", task)
            yield task


def get_old(dn: str, obj_id: str = None):
    """
    Returns old data of given dn or object id
    object id takes precedence over dn
    """
    dn = _normalized_dn(dn)
    with _get_session() as db_session:
        if obj_id:
            old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        else:
            old = db_session.query(Old).filter_by(dn=dn).first()
        if old:
            logger.info("Found old object %s", old)
            return deepcopy(old)
        else:
            logger.info("No old data found for %s", obj_id or dn)


def find_db_id(ox_context, username, build_cache_size):
    if build_cache_size and ox_context not in CACHE:
        logger.info(f"Building cache for {ox_context}")
        users = {}
        try:
            empty_objs = User.service(ox_context).list_all()
        except NoContextAdminPassword:
            logger.warning("... no password configured for context!")
        else:
            logger.info(f"Retrieved {len(empty_objs)} ids")

            def chunks(objs):
                return (
                    objs[pos : pos + build_cache_size]
                    for pos in range(0, len(objs), build_cache_size)
                )

            for chunk in chunks(empty_objs):
                soap_objs = User.service(ox_context).get_multiple_data(chunk)
                logger.info(f"Loaded {len(soap_objs) + len(users)}")
                for soap_obj in soap_objs:
                    users[soap_obj.name] = soap_obj.id
        logger.info("... built cache")
        CACHE[ox_context] = users
    if ox_context in CACHE:
        return CACHE[ox_context].get(username)
    try:
        user = get_obj_by_name_from_ox(User, ox_context, username)
    except NoContextAdminPassword:
        logger.warning("... no password configured for context!")
        return None
    if not user:
        logger.warning(f"{username}... not found!")
        return None
    return user.id


def get_all_old_objects(obj_id):
    oldies = []
    with _get_session() as db_session:
        oldies = db_session.query(Old).filter(Old.obj_id.like(obj_id)).all()
        for old in oldies:
            yield old


def get_all_old_users():
    oldies = []
    with _get_session() as db_session:
        oldies = db_session.query(Old).filter_by(udm_module="users/user").all()
        for old in oldies:
            yield old


def rewrite_ox_db_id(
    build_cache_size: int = 0,
    dry_run: bool = False,
):
    """
    Rewrites the oxDbId attribute for all users known to the Connector.
    This command iterates over all users and fetches the OX ID live from OX and
    then updates it in the OX Connector's old table.
    Users that are not found in OX will have their oxDbId removed.
    This may take a long time and depends on the amount of users in the OX App
    Suite database. You may speed things up by specifying a BUILD_CACHE_SIZE,
    although this may take a considerable amount of memory.
    """
    for old in get_all_old_users():
        attrs = deepcopy(json.loads(old.attrs))
        username = attrs.get("username", "")
        ox_context = attrs.get("oxContext", 10)
        cache_db_id = attrs.get("oxDbId", None)
        if not cache_db_id:
            continue
        ox_db_id = find_db_id(
            ox_context,
            username,
            build_cache_size=build_cache_size,
        )
        if not ox_db_id:
            logger.info(
                f"Removing oxDbId of {old} ({cache_db_id}): Not found in OX DB",
            )
            del attrs["oxDbId"]
        elif ox_db_id != cache_db_id:
            logger.info(
                f"Updating oxDbId of {old}: {cache_db_id} -> {ox_db_id}",
            )
            attrs["oxDbId"] = ox_db_id

        if not dry_run:
            old.attrs = json.dumps(attrs)


def create_task_from_old(obj_id: str):
    with _get_session() as db_session:
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            logger.info("Found old object %s", old)
            task = Task(
                obj_id=old.obj_id,
                udm_module=old.udm_module,
                dn=old.dn,
                attrs=old.attrs,
                status="retry",
            )
            db_session.add(task)
            db_session.commit()
            logger.info("Added task %s", task)
            open(LISTENER_DIR / "restart.json", "w")
        else:
            logger.info(
                "No old object found for %s; not creating any task",
                obj_id,
            )


def increment_error_count(task_id: int):
    """
    Increments the error count of that task by 1
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        task.num_errors += 1
        logger.info(
            "Task %s now has an error count of %d",
            task,
            task.num_errors,
        )
        return task.num_errors


def add_task(path: Path):
    """
    Adds the content of a JSON file as a new item to the tasks table.
    Note: PATH needs to be accessible from inside the OX Connector container,
    e.g., in /var/lib/univention-appcenter/apps/ox-connector/data/
    """
    logger.info("Parsing %s", path)
    with path.open() as file_handler:
        content = json.load(file_handler)
    udm_module = content["udm_object_type"]
    dn = _normalized_dn(content["dn"])
    attrs = content["object"]
    if attrs:
        obj_id = attrs.get("univentionObjectIdentifier")
    else:
        # should be univentionObjectIdentifier - therefore this line is more correct than
        # attrs.get("univentionObjectIdentifier"). but during the migration of old
        # tasks (json files) where the id was still entry_uuid, we better use
        # the univentionObjectIdentifier
        obj_id = content["id"]
    if not obj_id:
        logger.info(
            "Did not find univentionObjectIdentifier in %s. Skipping",
            path,
        )
        return
    enqueue_task(obj_id, udm_module, dn, attrs)
    (LISTENER_DIR / "restart.json").touch()


def enqueue_task(
    obj_id: str,
    udm_module: str,
    dn: str,
    attrs: dict,
):
    """
    Enqueue a provisioning task into the SQL tasks table directly.
    Used by the standalone K8s consumer to queue tasks from messages.
    """
    dn = _normalized_dn(dn)
    if not obj_id:
        logger.info("No obj_id provided, skipping task creation")
        return
    with _get_session() as db_session:
        task = Task(
            obj_id=obj_id,
            udm_module=udm_module,
            dn=dn,
            attrs=json.dumps(attrs),
        )
        db_session.add(task)
        db_session.commit()
        logger.info("Task %s created", task)


def add_old(path: Path):
    """
    Adds the content of a JSON file to the old table. If that item already
    exists (by univentionObjectIdentifier), it is updated, otherwise a new item
    is created.
    Note: PATH needs to be accessible from inside the OX Connector container,
    e.g., in /var/lib/univention-appcenter/apps/ox-connector/data/
    """
    logger.info("Parsing %s", path)
    with path.open() as file_handler:
        content = json.load(file_handler)
    udm_module = content["udm_object_type"]
    dn = _normalized_dn(content["dn"])
    attrs = content["object"]
    obj_id = attrs.get("univentionObjectIdentifier", "")
    if not obj_id:
        logger.info(
            "Did not find univentionObjectIdentifier in %s. Skipping",
            path,
        )
        return
    store_old(obj_id, udm_module, dn, attrs)


def remove_old(dn: str):
    """
    Removes an item from the old table.
    """
    if not dn:
        return
    with _get_session() as db_session:
        old = db_session.query(Old).filter_by(dn=dn).first()
        if old:
            logger.info("Removing %s", old)
            db_session.delete(old)
        else:
            logger.info("Removing old entry impossible, %s does not exist", dn)


def remove_task(task_id: str):
    """
    Removes an item from the tasks table.
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        if task:
            logger.info("Removing %s", task)
            db_session.delete(task)
        else:
            logger.info("Removing task impossible, %s does not exist", task_id)


def move_task_to_morgue(task_id: int, error_msg: str):
    """
    Move the task to the morgue table, meaning that it needs further, manual
    investigation. This can be used to unblock the connector. Removed from the
    tasks table.
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        dead = Dead(
            obj_id=task.obj_id,
            udm_module=task.udm_module,
            dn=task.dn,
            attrs=task.attrs,
            error_msg=error_msg,
        )
        db_session.add(dead)
        db_session.delete(task)
        db_session.commit()
        logger.info("Created morgue entry %s", dead)
        logger.info("Deleted task %s", task)


def move_task_to_old(task_id: int, attributes: dict = None):
    """
    Move the task to the old table, meaning that this data is now
    considered the last snapshot for further updates of this object. Removed
    from the list of the tasks table.
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        old = db_session.query(Old).filter_by(obj_id=task.obj_id).first()
        if attributes:
            attributes = json.dumps(attributes)
        else:
            attributes = task.attrs
        if old:
            if attributes:
                logger.info("Updating entry in old db %s", old)
                old.obj_id = task.obj_id
                old.udm_module = task.udm_module
                old.dn = task.dn
                old.attrs = attributes
                db_session.commit()
            else:
                logger.info("Removing entry in old db %s", old)
                db_session.delete(old)
        elif attributes:
            old = Old(
                obj_id=task.obj_id,
                udm_module=task.udm_module,
                dn=task.dn,
                attrs=attributes,
            )
            db_session.add(old)
            db_session.commit()
            logger.info("Created entry in old db %s", old)
        else:
            logger.info(
                "No old entry found while deleting task %s. Doing nothing",
                task,
            )
        for error in db_session.query(Dead).filter_by(obj_id=task.obj_id):
            logger.info("Removing %s", error)
            db_session.delete(error)
        db_session.delete(task)
        logger.info("Deleted task %s", task)


def get_errors(obj_id="*"):
    obj_id = obj_id.replace("*", "%")  # SQL LIKE
    with _get_session() as db_session:
        errors = (
            db_session.query(Dead)
            .filter(Dead.obj_id.like(obj_id))
            .order_by(Dead.id)
            .all()
        )
        for error in errors:
            yield error


def resync_item(obj_id):
    """
    An item is resynced using the latest data that is currently saved in UDM
    """
    items = chain(
        get_errors(obj_id=obj_id),
        get_all_old_objects(obj_id=obj_id),
    )
    for item in items:
        attrs = {
            "entry_uuid": item.obj_id,
            "dn": item.dn,
            "object_type": item.udm_module,
            "command": "m",
        }
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        filename = "%s/%s.json" % (
            "/var/lib/univention-appcenter/listener/ox-connector",
            timestamp,
        )
        with open(filename, "w") as fd:
            json.dump(attrs, fd, sort_keys=True, indent=4)
        logger.info("Resynced %s", item)
        return  # only needs to be done once
    logger.warn(
        "No Error for object ID %s found in database, resync not possible",
        obj_id,
    )


def retry_from_morgue(obj_id):
    """
    An item is retried to be synchronized by using the exact same data that
    was saved during the error occurance. Make sure that this item has not
    been / will not be synchronized with a more recent set of attributes as
    these would be overwritten by this retry (e.g., do not "retry" while a
    "resync" is still in the tasks db). If more than one item matches, all
    items are retried.
    """
    # TODO support obj_id and "db_id"?
    with _get_session() as db_session:
        errors = get_errors(obj_id=obj_id)
        for error in errors:
            task = Task(
                obj_id=error.obj_id,
                udm_module=error.udm_module,
                dn=error.dn,
                attrs=error.attrs,
                status="retry",
            )
            db_session.add(task)
            logger.info("Retrying %s", task)
        open(LISTENER_DIR / "restart.json", "w")


def remove_from_morgue(obj_id):
    """
    Remove an item from the morgue table. If more than one item matches, all
    items are removed.
    """
    # TODO support obj_id and "db_id"?
    with _get_session() as db_session:
        errors = list(get_errors(obj_id=obj_id))
        for error in errors:
            db_session.delete(error)
            logger.info("Removed error %s", error)


def search_morgue(
    obj_id: str = "*",
    output_format: str = "simple",
):
    """
    Search items in the morgue db. Items found can be printed in different
    formats ("simple" or "fuller" or "json")
    """
    errors = get_errors(obj_id=obj_id)
    json_output = []
    for error in errors:
        if output_format == "json":
            json_output.append(
                {
                    "db_id": error.id,
                    "univention_object_identifier": error.obj_id,
                    "dn": error.dn,
                    "udm_module": error.udm_module,
                    "attrs": json.loads(error.attrs),
                    "error": error.error_msg,
                },
            )
        if output_format in ["simple", "fuller"]:
            print("DN:", error.dn)
            print("Object Identifier:", error.obj_id)
            print("UDM module:", error.udm_module)
            print("ID (database):", error.id)
            print("Error occurred:", error.timestamp)
            if output_format == "simple":
                print("Error: ", error.error_msg.splitlines()[-1])
            else:
                print("Attributes:")
                for name, value in sorted(json.loads(error.attrs).items()):
                    print(" ", name, ":", value)
                print("Error:")
                for line in error.error_msg.splitlines():
                    print("  ", line)
            print("-")
    if output_format == "json":
        print(json.dumps(json_output, sort_keys=True, indent=2))


def search_tasks(output_format: str = "simple", first: bool = False):
    """
    Search items from the tasks database (queue of current tasks). Items found
    can be printed in different formats ("simple" or "fuller" or "json")
    """
    json_output = []
    for task in get_tasks():
        if output_format in ["simple", "fuller"]:
            print("DN:", task.dn)
            print("Object Identifier:", task.obj_id)
            print("UDM module:", task.udm_module)
            print("ID (database):", task.id)
            print("Created at:", task.created_at)
            print("Status:", task.status)
            print("Error count:", task.num_errors)
            if output_format == "fuller":
                print("Attributes:")
                for name, value in sorted(json.loads(task.attrs).items()):
                    print(" ", name, ":", value)
            print("-")

        if output_format == "json":
            json_output.append(
                {
                    "db_id": task.id,
                    "univention_object_identifier": task.obj_id,
                    "dn": task.dn,
                    "udm_module": task.udm_module,
                    "attrs": json.loads(task.attrs),
                    "num_errors": task.num_errors,
                },
            )
        if first:
            break
    if output_format == "json":
        print(json.dumps(json_output, sort_keys=True, indent=2))


def summarize_morgue(output_format: str = "simple"):
    """
    Shows a brief summary of the morgue table.
    Output can be either "simple", "fuller" or "json"
    """
    total = 0
    errors = {}
    for error in get_errors():
        total += 1
        errors.setdefault(error.udm_module, {})
        errors[error.udm_module][error.obj_id] = (
            errors[error.udm_module].get(error.obj_id, 0) + 1
        )
    if output_format == "json":
        print(
            json.dumps(
                errors
                | {
                    "total": total,
                },
                sort_keys=True,
                indent=2,
            ),
        )
    else:
        for module, ids in errors.items():
            num = 0
            for ob_id, error_count in ids.items():
                if output_format == "fuller":
                    print(f"  {ob_id}: {error_count}")
                num += error_count
            print(f"{module}: {num}")
            if output_format == "fuller":
                print("======")
        if errors and output_format == "simple":
            print("======")
        print(f"Total: {total}")


def summarize_tasks(output_format: str = "simple"):
    """
    Shows a brief summary of the tasks table (queue of current tasks).
    Output can be either "simple" or "json"
    """
    start_date = None
    end_date = None
    tasks = {}
    total = 0
    for task in get_tasks():
        if start_date is None:
            start_date = task.created_at
        end_date = task.created_at
        num = tasks.get(task.udm_module, 0)
        num += 1
        tasks[task.udm_module] = num
        total += 1
    if output_format == "json":
        print(
            json.dumps(
                tasks
                | {
                    "total": total,
                    "creation_start": str(start_date),
                    "creation_end": str(end_date),
                },
                sort_keys=True,
                indent=2,
            ),
        )
    else:
        for udm_module, num in tasks.items():
            print(f"{udm_module}: {num}")
        if tasks:
            print("======")
        print("Total:", total)
        if start_date and end_date:
            if start_date != end_date:
                print(f"Created between {start_date} and {end_date}")
            else:
                print(f"Created at {end_date}")


def export_old(obj_id: str):
    """
    Exports an item from the old table. It prints the item as JSON for you to
    save and examine. This file can be edited and re-added with the add-old
    command.
    """
    with _get_session() as db_session:
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if not old:
            return
        json_output = {
            "id": old.obj_id,
            "udm_object_type": old.udm_module,
            "dn": old.dn,
            "object": json.loads(old.attrs),
        }
        print(json.dumps(json_output, sort_keys=True, indent=2))


def search_old(obj_id: str, output_format: str = "simple"):
    """
    Search an item from the old table. It contains data the Connector has
    stored for item the last time it was processed successfully from the tasks
    table. Note: If the task was to delete, so was the item in the old table.
    Output can be either "simple" or "json".
    """
    with _get_session() as db_session:
        json_output = []
        obj_id = obj_id.replace("*", "%")  # SQL LIKE
        olds = db_session.query(Old).filter(Old.obj_id.like(obj_id)).all()
        for old in olds:
            if output_format == "json":
                json_output.append(
                    {
                        "id": old.obj_id,
                        "udm_object_type": old.udm_module,
                        "dn": old.dn,
                        "object": json.loads(old.attrs),
                    },
                )
            else:
                print("DN:", old.dn)
                print("Object Identifier:", old.obj_id)
                print("UDM module:", old.udm_module)
                print("ID (database):", old.id)
                print("Attributes:")
                for name, value in sorted(json.loads(old.attrs).items()):
                    print(" ", name, ":", value)
                print("-")
        if output_format == "json":
            print(json.dumps(json_output, sort_keys=True, indent=2))


def show_item(obj_id: str, output_format: str = "simple"):
    """
    Shows all rows in our tables that we got for an item. Other commands can
    give a more verbose output:
    * Last time it was synced successfully (see search-old)
    * Pending tasks that shall be processed (see search-tasks)
    * Current failures that may need interaction (see search-morgue)
    Output can be either "simple" or "json"
    """
    with _get_session() as db_session:
        json_output = {"old": {}, "tasks": [], "morgue": []}
        if output_format != "json":
            print("Searching for", obj_id)
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            if output_format == "json":
                json_output["old"] = {
                    "dn": old.dn,
                    "obj_id": old.obj_id,
                    "db_id": old.id,
                }
            else:
                print("Synced as", old)
        else:
            if output_format == "json":
                json_output["old"] = {}
            else:
                print("Not found as successfully synced")

        tasks = db_session.query(Task).filter_by(obj_id=obj_id)
        one_task = False
        for task in tasks:
            if not one_task:
                one_task = True
                if output_format == "json":
                    pass
                else:
                    print("Current tasks:")
            if output_format == "json":
                json_output["tasks"].append(
                    {
                        "dn": task.dn,
                        "obj_id": task.obj_id,
                        "db_id": task.id,
                    },
                )
            else:
                print("*", task)
        if not one_task:
            if output_format == "json":
                pass
            else:
                print("Currently no pending tasks")

        errors = db_session.query(Dead).filter_by(obj_id=obj_id)
        one_error = False
        for error in errors:
            if not one_error:
                one_error = True
                if output_format == "json":
                    pass
                else:
                    print("Current errors:")
            if output_format == "json":
                json_output["morgue"].append(
                    {
                        "dn": error.dn,
                        "obj_id": error.obj_id,
                        "db_id": error.id,
                    },
                )
            else:
                print("*", error)
        if not one_error:
            if output_format == "json":
                pass
            else:
                print("Currently no errors")
        if output_format == "json":
            print(json.dumps(json_output, sort_keys=True, indent=2))


def _normalized_dn(dn: str) -> str:
    """Returns the given DN in the format that it should be used (normalized, lowercase)"""
    if dn:
        return ldap.dn.dn2str(ldap.dn.str2dn(dn.lower()))


def _call(func, args):
    params = deepcopy(args.__dict__)
    params.pop("func")
    func(**params)


def _add_action(subparsers, func):
    import inspect
    from functools import partial

    name = func.__name__.replace("_", "-")
    description = func.__doc__
    subparser = subparsers.add_parser(
        name,
        description=description,
        help=description,
    )
    signature = inspect.signature(func)
    for name, param in signature.parameters.items():
        name = f"--{name.replace('_', '-')}"
        arg_params = {"required": param.default == inspect._empty}
        if not arg_params["required"]:
            arg_params["default"] = param.default
        if param.annotation in [Path, int]:
            arg_params["type"] = param.annotation
        if param.annotation is bool:
            store_action = (
                not param.default if param.default != inspect._empty else False
            )
            arg_params["action"] = f"store_{str(store_action).lower()}"
        subparser.add_argument(name, **arg_params)
    subparser.set_defaults(func=partial(_call, func))


def store_old(
    obj_id: str,
    udm_module: str,
    dn: str,
    attrs: dict,
):
    """
    Store an object in the old table. If that item already
    exists (by univentionObjectIdentifier), it is updated, otherwise a new item
    is created. Used by the standalone consumer.
    """
    dn = _normalized_dn(dn)
    attrs_json = json.dumps(attrs)
    with _get_session() as db_session:
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            logger.info("Updating old entry %s", old)
            old.obj_id = obj_id
            old.udm_module = udm_module
            old.dn = dn
            old.attrs = attrs_json
        else:
            old = Old(
                obj_id=obj_id,
                udm_module=udm_module,
                dn=dn,
                attrs=attrs_json,
            )
            db_session.add(old)
            logger.info("Created entry in old db %s", old)

        db_session.commit()


def delete_old(dn: str = None, obj_id: str = None):
    """
    Remove an item from the old table.
    Used by the standalone consumer.
    """
    if not dn and not obj_id:
        return
    dn = _normalized_dn(dn) if dn else None
    with _get_session() as db_session:
        if obj_id:
            old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        else:
            old = db_session.query(Old).filter_by(dn=dn).first()
        if old:
            logger.info("Removing old entry %s", old)
            db_session.delete(old)
            db_session.commit()
        else:
            logger.info(
                "Old entry not found for %s, nothing to remove",
                obj_id or dn,
            )


def store_relation(
    src_obj_id: str,
    src_udm_module: str,
    dst_obj_id: str,
    dst_udm_module: str,
    relation_name: str,
):
    """Add a relation between two old objects. Used by the standalone consumer."""
    relation = Relation(
        src_obj_id=src_obj_id,
        src_udm_module=src_udm_module,
        dst_obj_id=dst_obj_id,
        dst_udm_module=dst_udm_module,
        relation_name=relation_name,
    )
    logger.info("Adding relation %s", relation)
    with _get_session() as db_session:
        db_session.add(relation)
        db_session.add(relation)
        db_session.commit()


def remove_relation(src_obj_id: str, relation_name: str):
    """Remove all relations with a given src_obj_id and relation_name."""
    with _get_session() as db_session:
        for relation in (
            db_session.query(Relation)
            .filter_by(src_obj_id=src_obj_id, relation_name=relation_name)
            .all()
        ):
            logger.info("Deleting relation %s", relation)
            db_session.delete(relation)
        db_session.commit()


def get_relation_src(dst_obj_id: str, relation_name: str):
    """Yield the src_obj_id of every relation pointing to dst_obj_id."""
    with _get_session() as db_session:
        relations = (
            db_session.query(Relation)
            .filter_by(dst_obj_id=dst_obj_id, relation_name=relation_name)
            .all()
        )
        for relation in relations:
            logger.info("Found relation %s", relation)
            yield relation.src_obj_id


def initialize_db(set_permissions: bool = False):
    """
    Initialize the database: create all tables and validate schema.
    Returns True if initialization/success, raises on schema mismatch.
    """
    try:
        Base.metadata.create_all(engine)
        if set_permissions and DB_URL.drivername == "sqlite":
            os.chown(DB_URL.database, 0, 0)
            os.chmod(DB_URL.database, 0o640)

        logger.info("Database schema verified/created successfully")

        # Validate all expected tables exist
        inspector = sa_inspect(engine)
        expected_tables = {"tasks", "old", "morgue", "relations"}
        existing_tables = set(inspector.get_table_names())
        missing = expected_tables - existing_tables
        if missing:
            raise RuntimeError(
                f"Database schema invalid: missing tables: {missing}",
            )

        logger.info(
            "All expected tables present: %s",
            existing_tables & expected_tables,
        )
        return True
    except Exception:
        logger.exception("Database initialization failed")
        raise


@contextmanager
def _get_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.commit()
        db_session.flush()
        db_session.close()


if __name__ == "__main__":
    from argparse import ArgumentParser, RawTextHelpFormatter
    from logging.handlers import RotatingFileHandler
    import sys

    logger.setLevel("INFO")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    handler = RotatingFileHandler(
        "%s/univention-ox-connector-task-management.log" % LISTENER_DIR,
        maxBytes=1024 * 1024 * 500,
    )  # rotate after 500MB
    handler.setLevel("DEBUG")
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    help_text = """This program lets you manage the database of the OX Connector.
    There are three tables:
    tasks: Each row represents one current task of the Connector, it has not yet been successfully processed. Tasks are ordered by their creation time.
    old: Each row represents an object in the state it was synchronized successfully. Used when processing a task that references this object.
    morgue: Each row represents a task that failed to be synchronized with a certain error. These failed tasks will not be processed, they need to be individually examined by an administrator.
    """
    parser = ArgumentParser(
        description=help_text,
        formatter_class=RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        description="type %(prog)s <action> --help for further help and possible arguments",
        metavar="action",
    )
    _add_action(subparsers, show_item)
    _add_action(subparsers, resync_item)
    _add_action(subparsers, summarize_tasks)
    _add_action(subparsers, summarize_morgue)
    _add_action(subparsers, add_task)
    _add_action(subparsers, search_tasks)
    _add_action(subparsers, move_task_to_old)
    _add_action(subparsers, move_task_to_morgue)
    _add_action(subparsers, add_old)
    _add_action(subparsers, export_old)
    _add_action(subparsers, search_old)
    _add_action(subparsers, search_morgue)
    _add_action(subparsers, remove_from_morgue)
    _add_action(subparsers, retry_from_morgue)
    _add_action(subparsers, rewrite_ox_db_id)
    # TODO: check_sync_status.py: See the CLI update-ox-db-cache - it compares live OX DB with UDM

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
    else:
        logger.debug("Running CLI with args %r", sys.argv)
        args.func(args)
