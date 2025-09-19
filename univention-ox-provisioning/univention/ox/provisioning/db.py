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
import pprint
import json
from pathlib import Path
import datetime
from contextlib import contextmanager
from copy import deepcopy
from pwd import getpwnam

import ldap.dn

from sqlalchemy import create_engine, Column, Integer, String, insert, update, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# db_password = os.environ["DB_PASSWORD"]
# docker_host_name = os.environ["DOCKER_HOST_NAME"]
# engine = create_engine(f"postgresql+psycopg2://ox-connector:{db_password}@{docker_host_name}:5432/ox-connector")

LISTENER_DIR = Path("/var/lib/univention-appcenter/apps/ox-connector/data/listener/")

engine = create_engine("sqlite:///%s/db.sqlite" % LISTENER_DIR)
listener_uid = getpwnam('listener').pw_uid
os.chown(f"{LISTENER_DIR}/db.sqlite", listener_uid, -1)
os.chmod(f"{LISTENER_DIR}/db.sqlite", 0o640)

logger = logging.getLogger("listener")


class Dead(Base):
    __tablename__ = "rejected_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)
    error_msg = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (Index("rejected_tasks_obj_id", "obj_id"), )

    def __str__(self):
        return f"{self.dn} ({self.obj_id}; {self.udm_module}; {self.__tablename__}:{self.id})"

class Old(Base):
    __tablename__ = "old_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)

    __table_args__ = (Index("old_entries_obj_id", "obj_id"), Index("old_entries_dn", "dn"), )

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

    __table_args__ = (Index("tasks_created_at", "created_at"), )

    def __str__(self):
        return f"{self.dn} ({self.obj_id}; {self.udm_module}; {self.__tablename__}:{self.id})"


Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)


def get_tasks(udm_module: str=None, filter_empty_attributes: bool=None):
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


def get_old(dn: str, obj_id: str=None):
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
            logger.info("No old data found for %s", dn)


def create_task_from_old(obj_id: str):
    with _get_session() as db_session:
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            logger.info("Found old object %s", old)
            task = Task(obj_id=old.obj_id, udm_module=old.udm_module, dn=old.dn, attrs=old.attrs, status="retry")
            db_session.add(task)
            db_session.commit()
            logger.info("Added task %s", task)
            open(LISTENER_DIR / "restart.json", "w")
        else:
            logger.info("No old object found for %s; not creating any task", obj_id)


def increment_error_count(task_id: int):
    """
    Increments the error count of that task by 1
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        task.num_errors += 1
        logger.info("Task %s now has an error count of %d", task, task.num_errors)


def add_task(path: Path):
    """
    Adds the content of a JSON file to the queue of tasks
    """
    logger.info("Parsing %s", path)
    with path.open() as file_handler:
        content = json.load(file_handler)
    udm_module = content["udm_object_type"]
    dn = _normalized_dn(content["dn"])
    attrs = content["object"]
    obj_id = content["id"]
    with _get_session() as db_session:
        task = Task(obj_id=obj_id, udm_module=udm_module, dn=dn, attrs=json.dumps(attrs))
        db_session.add(task)
        db_session.commit()
        logger.info("Task %s created", task)
    open(LISTENER_DIR / "restart.json", "w")


def add_old(path: Path):
    """
    Adds the content of a JSON file to the database of already seen objects
    ("old db")
    """
    logger.info("Parsing %s", path)
    with path.open() as file_handler:
        content = json.load(file_handler)
    udm_module = content["udm_object_type"]
    dn = _normalized_dn(content["dn"])
    attrs = content["object"]
    obj_id = attrs.get("univentionObjectIdentifier", "")
    if not obj_id:
        logger.info("Did not find univentionObjectIdentifier in %s. Skipping", path)
        return
    with _get_session() as db_session:
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            logger.info("Found old data %s", old)
            old.obj_id = obj_id
            old.udm_module = udm_module
            old.dn = dn
            old.attrs = json.dumps(attrs)
            logger.info("Updating...")
        else:
            old = Old(obj_id=obj_id, udm_module=udm_module, dn=dn, attrs=json.dumps(attrs))
            db_session.add(old)
            db_session.commit()
            logger.info("Created entry in old db %s", old)


def remove_old(dn: str):
    """
    Removes an entry from the "old db"
    """
    if not dn:
        return
    with _get_session() as db_session:
        old = db_session.query(Old).filter_by(dn=dn).first()
        if old:
            logger.info("Removing %s", old)
            db_session.delete(old)
        else:
            logger.info("Removing old entry impossible, %s does not exist", obj_id)


def remove_task(task_id: str):
    """
    Removes an entry from the active tasks.
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
    Move the task to the "dead queue", meaning that it needs further, manual
    investigation. This can be used to unblock the connector. Removed from the list of active tasks.
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        dead = Dead(obj_id=task.obj_id, udm_module=task.udm_module, dn=task.dn, attrs=task.attrs, error_msg=error_msg)
        db_session.add(dead)
        db_session.delete(task)
        db_session.commit()
        logger.info("Created morgue entry %s", dead)
        logger.info("Deleted task %s", task)


def move_task_to_old(task_id: int, attributes: dict=None):
    """
    Move the task to the "old database", meaning that this data is now
    considered the last snapshot for further updates of this object. Removed
    from the list of active tasks.
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
            else:
                logger.info("Removing entry in old db %s", old)
                db_session.delete(old)
        elif attributes:
            old = Old(obj_id=task.obj_id, udm_module=task.udm_module, dn=task.dn, attrs=attributes)
            db_session.add(old)
            db_session.commit()
            logger.info("Created entry in old db %s", old)
        else:
            logger.info("No old entry found while deleting task %s. Doing nothing", task)
        for error in db_session.query(Dead).filter_by(obj_id=task.obj_id):
            logger.info("Removing %s", error)
            db_session.delete(error)
        db_session.delete(task)
        logger.info("Deleted task %s", task)

def get_errors(obj_id='*'):
    obj_id = obj_id.replace("*", "%")  # SQL LIKE
    with _get_session() as db_session:
        errors = db_session.query(Dead).filter(Dead.obj_id.like(obj_id)).all()
        for error in errors:
            yield error

def resync_object(obj_id):
    """
    Objects are resynced using the new object data that is currently saved in
    UDM
    """
    # TODO: maybe we want to search in old, too? Resyncing may make sense from old, too? Probably search in errors first? (DN is "more recent")
    errors = get_errors(obj_id=obj_id)
    for error in errors:
        attrs = {
            "entry_uuid": error.obj_id,
            "dn": error.dn,
            "object_type": error.udm_module,
            "command": "m",
        }
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
        filename = '%s/%s.json' % ("/var/lib/univention-appcenter/listener/ox-connector", timestamp)
        logger.info("Resynced %s", error)
        break  # only needs to be done once
    with open(filename, "w") as fd:
        json.dump(attrs, fd, sort_keys=True, indent=4)


def retry_rejected(obj_id):
    """
    Objects are retried using the exact same data that was saved during the
    error occurance
    """
    # TODO support obj_id and "db_id"?
    with _get_session() as db_session:
        errors = get_errors(obj_id=obj_id)
        for error in errors:
            task = Task(obj_id=error.obj_id, udm_module=error.udm_module, dn=error.dn, attrs=error.attrs, status="retry")
            db_session.add(task)
        logger.info("Retrying %s", task)
        open(LISTENER_DIR / "restart.json", "w")

def remove_rejected(obj_id):
    """
    Remove all items from the "error queue" that belong to a specific object.
    """
    # TODO support obj_id and "db_id"?
    with _get_session() as db_session:
        errors = get_errors(obj_id=obj_id)
        for error in errors:
            db_session.delete(error)
            logger.info("Removed error %s", error)

def list_rejected(obj_id: str="*", output_format: str="simple"):
    """
    List objects in the "error queue". Objects found can be printed in different formats
    ("simple" or "fuller" or "json")
    """
    errors = get_errors(obj_id=obj_id)
    json_output = []
    for error in errors:
        if output_format == "json":
            json_output.append({
                "db_id": error.id,
                "univention_object_identifier": error.obj_id,
                "dn": error.dn,
                "udm_module": error.udm_module,
                "attrs": json.loads(error.attrs),
                "error": error.error_msg,
            })
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
    if json_output:
        print(json.dumps(json_output, sort_keys=True, indent=2))


def list_tasks(output_format: str="simple"):
    """
    List objects in the "currrent tasks queue". Objects found can be printed in
    different formats ("simple" or "fuller" or "json")
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
            json_output.append({
                "db_id": error.id,
                "univention_object_identifier": error.obj_id,
                "dn": error.dn,
                "udm_module": error.udm_module,
                "attrs": json.loads(error.attrs),
                "error": error.error_msg,
            })
        if json_output:
            print(json.dumps(json_output, sort_keys=True, indent=2))


def show_summary(output_format: str="simple"):
    """
    Shows the current size of to be processed tasks. Output can be "simple"
    readable or "json".
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
        print(json.dumps(tasks | {
            "total": total,
            "creation_start": str(start_date),
            "creation_end": str(end_date),
        }, sort_keys=True, indent=2))
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


def show_old(obj_id: str, output_format: str="simple"):
    """
    Shows data the Connector has stored for that object
    It has been saved the last time the object was processed
    successfully. If the object has been deleted, so was this data
    """
    with _get_session() as db_session:
        json_output = []
        obj_id = obj_id.replace("*", "%")  # SQL LIKE
        olds = db_session.query(Old).filter(Old.obj_id.like(obj_id)).all()
        for old in olds:
            if output_format == "json":
                json_output.append(json.loads(old))
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

def search_for(obj_id: str, output_format: str="simple"):
    """
    Shows all we got for an object:
    * Last time it was synced successfully
    * Pending tasks that shall be processed
    * Current failures that may need interaction (see list_rejected)
    """
    with _get_session() as db_session:
        if output_format != "json":
            print("Searching for", obj_id)
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            if output_format == "json":
                pass
            else:
                print("Synced as", old)
        else:
            if output_format == "json":
                pass
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
                pass
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
                pass
            else:
                print("*", error)
        if not one_error:
            if output_format == "json":
                pass
            else:
                print("Currently no errors")


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
    subparser = subparsers.add_parser(name, description=description, help=description)
    signature = inspect.signature(func)
    for name, param in signature.parameters.items():
        name = f"--{name.replace('_', '-')}"
        arg_params = {"required": param.default == inspect._empty}
        if not arg_params["required"]:
            arg_params["default"] = param.default
        if param.annotation in [Path, int, bool]:
            arg_params["type"] = param.annotation
        subparser.add_argument(name, **arg_params)
    subparser.set_defaults(func=partial(_call, func))


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
    from argparse import ArgumentParser
    import sys

    logger.setLevel("INFO")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    handler = logging.FileHandler("/var/lib/univention-appcenter/apps/ox-connector/data/db.log")
    handler.setLevel("DEBUG")
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(description='type %(prog)s <action> --help for further help and possible arguments', metavar='action')
    _add_action(subparsers, add_task)
    _add_action(subparsers, add_old)
    _add_action(subparsers, move_task_to_old)
    _add_action(subparsers, move_task_to_morgue)
    _add_action(subparsers, list_rejected)
    _add_action(subparsers, remove_rejected)
    _add_action(subparsers, retry_rejected)
    _add_action(subparsers, list_tasks)
    _add_action(subparsers, resync_object)
    _add_action(subparsers, show_summary)
    _add_action(subparsers, search_for)
    _add_action(subparsers, show_old)
    # TODO: rebuild_cache: See the CLI update-ox-db-cache - it basically retrieves all OxDbIds again from the live OX DB...
    # TODO: check_sync_status.py: See the CLI update-ox-db-cache - it compares live OX DB with UDM

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
    else:
        logger.debug("Running CLI with args %r", sys.argv)
        args.func(args)
