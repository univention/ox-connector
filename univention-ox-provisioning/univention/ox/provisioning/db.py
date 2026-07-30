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
import json
from pathlib import Path
from itertools import chain
import datetime
from copy import deepcopy


from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Index,
)
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy import inspect as sa_inspect

from lancelog import logger
from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.soap.config import NoContextAdminPassword
from univention.ox.provisioning.helpers import (
    get_obj_by_name_from_ox,
    normalized_dn,
)

Base = declarative_base()

LISTENER_DIR = Path(
    "/var/lib/univention-appcenter/apps/ox-connector/data/listener/",
)


def get_db_url():
    db_connection_string = os.environ.get("OX_CONNECTOR_DB")

    if db_connection_string is None:
        raise ValueError("OX_CONNECTOR_DB environment variable must be set")

    return make_url(db_connection_string)


DB_URL = get_db_url()
engine = create_engine(DB_URL)

User = get_ox_integration_class("SOAP", "User")
CACHE = {}


class Relation(Base):
    __tablename__ = "relations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    src_obj_id = Column(
        String,
        nullable=False,
    )
    src_udm_module = Column(String, nullable=False)
    dst_obj_id = Column(
        String,
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
    attrs = Column(String, nullable=True)
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
        primaryjoin="foreign(Relation.src_obj_id) == Old.obj_id",
        cascade="delete",
    )
    backward_relations = relationship(
        "Relation",
        primaryjoin="foreign(Relation.dst_obj_id) == Old.obj_id",
        cascade="delete",
    )

    __table_args__ = (
        Index("old_obj_id", "obj_id", unique=True),
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
    attrs = Column(String, nullable=True)
    status = Column(String, nullable=False, default="new")
    num_errors = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (Index("tasks_created_at", "created_at"),)

    def __str__(self):
        return f"{self.dn} ({self.obj_id}; {self.udm_module}; {self.__tablename__}:{self.id})"


class DBSession:
    """Context-aware database session with explicit commit control.

    Usage as context manager (auto-commit on success, rollback on exception):
        with DBSession() as db:
            db.store_old(obj_id, module, dn, attrs)
            db.add_relation(...)
        # commit happens automatically here

    Usage with manual commit:
        with DBSession() as db:
            db.store_old(obj_id, module, dn, attrs)
            db.commit()  # explicit commit

        db = DBSession()
        try:
            db.store_old(obj_id, module, dn, attrs)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    """

    def __init__(self):
        self.session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
        return False

    def commit(self):
        """Commit all changes to the database."""
        self.session.commit()

    def rollback(self):
        """Rollback all changes."""
        self.session.rollback()

    def close(self):
        """Close the session."""
        self.session.close()

    def add(self, obj):
        """Add an object to the session."""
        self.session.add(obj)

    def delete(self, obj):
        """Delete an object from the session."""
        self.session.delete(obj)

    def query(self, model):
        """Return a query for the given model."""
        return self.session.query(model)

    # ---- Relation operations ----

    def add_relation(
        self,
        src_obj_id,
        src_udm_module,
        dst_obj_id,
        dst_udm_module,
        relation_name,
    ):
        """Add a Relation object."""
        relation = Relation(
            src_obj_id=src_obj_id,
            src_udm_module=src_udm_module,
            dst_obj_id=dst_obj_id,
            dst_udm_module=dst_udm_module,
            relation_name=relation_name,
        )
        logger.info("Adding relation", relation=relation)
        self.session.add(relation)

    def remove_relation(self, src_obj_id, relation_name):
        """Remove all relations with a given src_obj_id and relation_name."""
        for relation in (
            self.session.query(Relation)
            .filter_by(src_obj_id=src_obj_id, relation_name=relation_name)
            .all()
        ):
            logger.info("Deleting relation", relation=relation)
            self.session.delete(relation)

    def get_relation_src(self, dst_obj_id, relation_name):
        """Yield the src_obj_id of every relation pointing to dst_obj_id."""
        for relation in (
            self.session.query(Relation)
            .filter_by(dst_obj_id=dst_obj_id, relation_name=relation_name)
            .all()
        ):
            logger.info("Found relation", relation=relation)
            yield relation.src_obj_id

    # ---- Task operations ----

    def contain_tasks(self):
        return self.session.query(Task).count() > 0

    def get_task(self, obj_id=None):
        """Return the first pending task with a given obj_id."""
        if obj_id is None:
            return None
        return self.session.query(Task).filter_by(obj_id=obj_id).first()

    def get_tasks(self, udm_module=None, filter_empty_attributes=None):
        """Return all tasks sorted by creation time."""
        tasks = self.session.query(Task)
        if udm_module:
            tasks = tasks.filter_by(udm_module=udm_module)
        if filter_empty_attributes is True:
            tasks = tasks.filter(Task.attrs.is_(None))
        elif filter_empty_attributes is False:
            tasks = tasks.filter(Task.attrs.is_not(None))
        for task in tasks.order_by(Task.created_at):
            logger.debug("Yielding task", task=task)
            yield task

    def enqueue_task(self, obj_id, udm_module, dn, attrs):
        """Enqueue a provisioning task into the SQL tasks table."""
        dn = normalized_dn(dn)
        if not obj_id:
            logger.info("No obj_id provided, skipping task creation")
            return
        task = Task(
            obj_id=obj_id,
            udm_module=udm_module,
            dn=dn,
            attrs=json.dumps(attrs) if attrs else None,
        )
        self.session.add(task)
        logger.info("Task created", task=task)

    def remove_task(self, task_id):
        """Remove an item from the tasks table."""
        task = self.session.query(Task).get(task_id)
        if task:
            logger.info("Removing task", task=task)
            self.session.delete(task)
        else:
            logger.info(
                "Removing task impossible, task does not exist",
                task_id=task_id,
            )

    def move_task_to_morgue(self, task_id, error_msg):
        """Move the task to the morgue table."""
        task = self.session.query(Task).get(task_id)
        dead = Dead(
            obj_id=task.obj_id,
            udm_module=task.udm_module,
            dn=task.dn,
            attrs=task.attrs,
            error_msg=error_msg,
        )
        self.session.add(dead)
        self.session.delete(task)
        logger.info("Created morgue entry", entry=dead)
        logger.info("Deleted task", task=task)

    def move_task_to_old(self, task_id, attributes=None):
        """Move the task to the old table."""
        task = self.session.query(Task).get(task_id)
        if task is None:
            return

        old = self.session.query(Old).filter_by(obj_id=task.obj_id).first()
        if attributes:
            attributes = json.dumps(attributes)
        else:
            attributes = task.attrs

        if old:
            if attributes:
                logger.info("Updating entry in old db", entry=old)
                old.obj_id = task.obj_id
                old.udm_module = task.udm_module
                old.dn = task.dn
                old.attrs = attributes
            else:
                logger.info("Removing entry in old db", entry=old)
                self.session.delete(old)
        elif attributes:
            old = Old(
                obj_id=task.obj_id,
                udm_module=task.udm_module,
                dn=task.dn,
                attrs=attributes,
            )
            self.session.add(old)
            logger.info("Created entry in old db", entry=old)
        else:
            logger.info(
                "No old entry found while deleting task. Doing nothing",
                task=task,
            )

        for error in self.session.query(Dead).filter_by(obj_id=task.obj_id):
            logger.info("Removing entry", entry=error)
            self.session.delete(error)

        self.session.delete(task)
        logger.info("Deleted task", task=task)

    # ---- Old object operations ----

    def contain_old(self):
        return self.session.query(Old).count() > 0

    def get_old(self, dn, obj_id=None):
        """Return old data of given dn or object id. Object id takes precedence."""
        dn = normalized_dn(dn)
        if obj_id:
            old = self.session.query(Old).filter_by(obj_id=obj_id).first()
        else:
            old = self.session.query(Old).filter_by(dn=dn).first()
        if old:
            logger.info("Found old object", object=old)
            return deepcopy(old)
        else:
            logger.info("No old data found", id=obj_id or dn)

    def get_all_old_objects(self, obj_id):
        """Yield all old objects matching obj_id."""
        oldies = self.session.query(Old).filter(Old.obj_id.like(obj_id)).all()
        for old in oldies:
            yield old

    def get_all_old_users(self):
        """Yield all old user objects."""
        oldies = (
            self.session.query(Old).filter_by(udm_module="users/user").all()
        )
        for old in oldies:
            yield old

    def store_old(self, obj_id, udm_module, dn, attrs):
        """Store an object in the old table (upsert).

        If the item already exists (by univentionObjectIdentifier), it is updated.
        Otherwise, a new item is created. Used by the standalone consumer.
        """
        dn = normalized_dn(dn)
        attrs_json = json.dumps(attrs)
        old = self.session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            logger.info("Updating old entry", entry=old)
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
            self.session.add(old)
            logger.info("Created entry in old db", entry=old)

    def delete_old(self, dn=None, obj_id=None):
        """Remove an item from the old table. Used by the standalone consumer."""
        if not dn and not obj_id:
            return
        dn = normalized_dn(dn) if dn else None
        if obj_id:
            old = self.session.query(Old).filter_by(obj_id=obj_id).first()
        else:
            old = self.session.query(Old).filter_by(dn=dn).first()
        if old:
            logger.info("Removing old entry", entry=old)
            self.session.delete(old)
        else:
            logger.info(
                "Old entry not found, nothing to remove",
                id=obj_id or dn,
            )

    # ---- Morgue (Dead) operations ----

    def get_errors(self, obj_id="*"):
        """Yield error entries from the morgue table."""
        obj_id = obj_id.replace("*", "%")  # SQL LIKE
        errors = (
            self.session.query(Dead)
            .filter(Dead.obj_id.like(obj_id))
            .order_by(Dead.id)
            .all()
        )
        for error in errors:
            yield error

    def retry_from_morgue(self, obj_id):
        """Retry items from the morgue table."""
        for error in self.get_errors(obj_id=obj_id):
            task = Task(
                obj_id=error.obj_id,
                udm_module=error.udm_module,
                dn=error.dn,
                attrs=error.attrs,
                status="retry",
            )
            self.session.add(task)
            logger.info("Retrying task", task=task)
        open(LISTENER_DIR / "restart.json", "w")

    def remove_from_morgue(self, obj_id):
        """Remove items from the morgue table."""
        for error in self.get_errors(obj_id=obj_id):
            self.session.delete(error)
            logger.info("Removed error", error=error)

    # ---- Display helpers (used by CLI) ----

    def summarize_tasks(self, output_format="simple"):
        """Show a brief summary of the tasks table."""
        start_date = None
        end_date = None
        tasks = {}
        total = 0
        for task in self.get_tasks():
            if start_date is None:
                start_date = task.created_at
            end_date = task.created_at
            num = tasks.get(task.udm_module, 0) + 1
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

    def summarize_morgue(self, output_format="simple"):
        """Show a brief summary of the morgue table."""
        total = 0
        errors = {}
        for error in self.get_errors():
            total += 1
            errors.setdefault(error.udm_module, {})
            errors[error.udm_module][error.obj_id] = (
                errors[error.udm_module].get(error.obj_id, 0) + 1
            )
        if output_format == "json":
            print(
                json.dumps(
                    errors | {"total": total},
                    sort_keys=True,
                    indent=2,
                ),
            )
        else:
            for module, ids in errors.items():
                num = sum(ids.values())
                print(f"{module}: {num}")
                if output_format == "fuller":
                    for ob_id, error_count in ids.items():
                        print(f"  {ob_id}: {error_count}")
                    print("======")
            if errors and output_format == "simple":
                print("======")
            print(f"Total: {total}")

    def show_item(self, obj_id, output_format="simple"):
        """Show all rows in all tables for an item."""
        json_output = {"old": {}, "tasks": [], "morgue": []}
        if output_format != "json":
            print("Searching for", obj_id)

        old = self.session.query(Old).filter_by(obj_id=obj_id).first()
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

        tasks = self.session.query(Task).filter_by(obj_id=obj_id)
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
                    {"dn": task.dn, "obj_id": task.obj_id, "db_id": task.id},
                )
            else:
                print("*", task)
        if not one_task:
            if output_format == "json":
                pass
            else:
                print("Currently no pending tasks")

        errors = self.session.query(Dead).filter_by(obj_id=obj_id)
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

    def find_db_id(self, ox_context, username, build_cache_size):
        """Find the database ID for a user in a given context."""
        if build_cache_size and ox_context not in CACHE:
            logger.info("Building cache for context", context=ox_context)
            users = {}
            try:
                empty_objs = User.service(ox_context).list_all()
            except NoContextAdminPassword:
                logger.warning("... no password configured for context!")
            else:
                logger.info("Retrieved ids", count=len(empty_objs))

                def chunks(objs):
                    return (
                        objs[pos : pos + build_cache_size]
                        for pos in range(0, len(objs), build_cache_size)
                    )

                for chunk in chunks(empty_objs):
                    soap_objs = User.service(ox_context).get_multiple_data(
                        chunk,
                    )
                    logger.info(
                        "Loaded objects",
                        count=len(soap_objs) + len(users),
                    )
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
            logger.warning("User not found", username=username)
            return None
        return user.id

    def rewrite_ox_db_id(
        self,
        build_cache_size: int = 0,
        dry_run: bool = False,
    ):
        """Rewrite the oxDbId attribute for all users known to the Connector."""
        for old in self.get_all_old_users():
            attrs = deepcopy(json.loads(old.attrs))
            username = attrs.get("username", "")
            ox_context = attrs.get("oxContext", 10)
            cache_db_id = attrs.get("oxDbId", None)
            if not cache_db_id:
                continue
            ox_db_id = self.find_db_id(
                ox_context,
                username,
                build_cache_size=build_cache_size,
            )
            if not ox_db_id:
                logger.info(
                    "Removing oxDbId: Not found in OX DB",
                    old=old,
                    cache_db_id=cache_db_id,
                )
                del attrs["oxDbId"]
            elif ox_db_id != cache_db_id:
                logger.info(
                    "Updating oxDbId",
                    old=old,
                    cache_db_id=cache_db_id,
                    ox_db_id=ox_db_id,
                )
                attrs["oxDbId"] = ox_db_id

            if not dry_run:
                old.attrs = json.dumps(attrs)

    def resync_item(self, obj_id):
        """Resync an item using the latest data saved in UDM."""
        for item in chain(
            self.get_errors(obj_id=obj_id),
            self.get_all_old_objects(obj_id=obj_id),
        ):
            attrs = {
                "entry_uuid": item.obj_id,
                "dn": item.dn,
                "object_type": item.udm_module,
                "command": "m",
            }
            timestamp = datetime.datetime.now().strftime(
                "%Y-%m-%d-%H-%M-%S-%f",
            )
            filename = (
                "/var/lib/univention-appcenter/listener/ox-connector/%s.json"
                % timestamp
            )
            with open(filename, "w") as fd:
                json.dump(attrs, fd, sort_keys=True, indent=4)
            logger.info("Resynced item", item=item)
            return
        logger.warning(
            "No error for object ID found in database, resync not possible",
            obj_id=obj_id,
        )

    def create_task_from_old(self, obj_id):
        """Create a retry task from an old object."""
        old = self.session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            logger.info("Found old object", old=old)
            task = Task(
                obj_id=old.obj_id,
                udm_module=old.udm_module,
                dn=old.dn,
                attrs=old.attrs,
                status="retry",
            )
            self.session.add(task)
            logger.info("Added task", task=task)
            open(LISTENER_DIR / "restart.json", "w")
        else:
            logger.info(
                "No old object found; not creating any task",
                obj_id=obj_id,
            )

    def increment_error_count(self, task_id):
        """Increment the error count of that task by 1."""
        task = self.session.query(Task).get(task_id)
        task.num_errors += 1
        logger.info(
            "Task error count incremented",
            task=task,
            num_errors=task.num_errors,
        )
        return task.num_errors

    def search_src_of_relation(self, dst_obj_id, relation_name):
        """Yield the src_obj_id of every relation pointing to dst_obj_id with the given relation_name."""
        relations = (
            self.session.query(Relation)
            .filter_by(dst_obj_id=dst_obj_id, relation_name=relation_name)
            .all()
        )
        result = [r.src_obj_id for r in relations]
        for relation in relations:
            logger.info("Found relation", relation=relation)
        yield from result

    def remove_old(self, dn: str):
        """Remove an item from the old table."""
        self.delete_old(dn=dn)


def initialize_db(
    set_permissions: bool = False,
    create_parent_directory: bool = False,
):
    """Initialize the database: create all tables and validate schema."""
    try:
        if create_parent_directory and DB_URL.drivername == "sqlite":
            Path(DB_URL.database).parent.mkdir(parents=True, exist_ok=True)

        Base.metadata.create_all(engine)
        if set_permissions and DB_URL.drivername == "sqlite":
            os.chown(DB_URL.database, 0, 0)
            os.chmod(DB_URL.database, 0o640)

        logger.info("Database schema verified/created successfully")

        inspector = sa_inspect(engine)
        expected_tables = {"tasks", "old", "morgue", "relations"}
        existing_tables = set(inspector.get_table_names())
        missing = expected_tables - existing_tables
        if missing:
            raise RuntimeError(
                f"Database schema invalid: missing tables: {missing}",
            )

        logger.info(
            "All expected tables present",
            tables=existing_tables & expected_tables,
        )
        return True
    except Exception:
        logger.exception("Database initialization failed")
        raise
