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

import ldap.dn

from sqlalchemy import create_engine, Column, Integer, String, insert, update, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

db_password = os.environ["DB_PASSWORD"]
docker_host_name = os.environ["DOCKER_HOST_NAME"]
engine = create_engine(f"postgresql+psycopg2://ox-connector:{db_password}@{docker_host_name}:5432/ox-connector")


logger = logging.getLogger("listener")


class Dead(Base):
    __tablename__ = "rejected_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)
    error_msg = Column(String, nullable=False)

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
    ox_db_id = Column(Integer, nullable=True)

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


def get_tasks():
    """
    Return all tasks sorted by creation time.
    """
    with _get_session() as db_session:
        for task in db_session.query(Task).order_by(Task.created_at):
            logger.info("Yielding task %s", task)
            yield task


def get_old(dn: str):
    """
    Returns old data of given object id
    """
    dn = _normalized_dn(dn)
    with _get_session() as db_session:
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


def move_task_to_dead_letters(task_id: int, error_msg: str):
    """
    Move the task to the "dead queue", meaning that it needs further, manual
    investigation. Removed from the list of active tasks.
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        dead = Dead(obj_id=task.obj_id, udm_module=task.udm_module, dn=task.dn, attrs=task.attrs, error_msg=error_msg)
        db_session.add(dead)
        db_session.delete(task)
        db_session.commit()
        logger.info("Created dead letter entry %s", dead)
        logger.info("Deleted task %s", task)


def move_task_to_old(task_id: int, ox_db_id: int=None):
    """
    Move the task to the "old database", meaning that this data is now
    considered the last snapshot for further updates of this object. Removed
    from the list of active tasks.
    """
    with _get_session() as db_session:
        task = db_session.query(Task).get(task_id)
        old = db_session.query(Old).filter_by(obj_id=task.obj_id).first()
        if old:
            logger.info("Updating entry in old db %s", old)
            old.obj_id = task.obj_id
            old.udm_module = task.udm_module
            old.dn = task.dn
            old.attrs = task.attrs
            old.ox_db_id = ox_db_id
        else:
            old = Old(obj_id=task.obj_id, udm_module=task.udm_module, dn=task.dn, attrs=task.attrs, ox_db_id=ox_db_id)
            db_session.add(old)
            db_session.commit()
            logger.info("Created entry in old db %s", old)
        for error in db_session.query(Dead).filter_by(obj_id=task.obj_id):
            db_session.delete(error)
        db_session.delete(task)
    logger.info("Deleted task %s", task)


def filter_error(obj_id, print_json: bool=True, retry: bool=False, fresh_resync: bool=False, delete: bool=False):
    """
    Filter in the "dead queue". Objects found can be printed, retried (the
    exact same data are moved to the list of active tasks), fresh resync (this
    object is freshly added from the leading database to the list of active
    tasks), delete (error is deleted; makes sense to combine this with retry or
            resync)
    """
    with _get_session() as db_session:
        obj_id = obj_id.replace("*", "%")  # SQL LIKE
        errors = db_session.query(Dead).filter(Dead.obj_id.like(obj_id)).all()
        for error in errors:
            if print_json:
                print(json.dumps({
                    "db_id": error.id,
                    "univention_object_identifier": error.obj_id,
                    "dn": error.dn,
                    "udm_module": error.udm_module,
                    "attrs": json.loads(error.attrs),
                    "error": error.error_msg,
                }, sort_keys=True, indent=2))
            if retry:
                task = Task(obj_id=error.obj_id, udm_module=error.udm_module, dn=error.dn, attrs=error.attrs, status="retry")
                db_session.add(task)
            if fresh_resync:
                attrs = {
                    "entry_uuid": error.obj_id,
                    "dn": error.dn,
                    "object_type": error.udm_module,
                    "command": "m",
                }
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
                filename = '%s/%s.json' % ("/var/lib/univention-appcenter/listener/ox-connector", timestamp)

                with open(filename, "w") as fd:
                    json.dump(attrs, fd, sort_keys=True, indent=4)
            if delete:
                db_session.delete(error)


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
    _add_action(subparsers, move_task_to_dead_letters)
    _add_action(subparsers, filter_error)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
    else:
        logger.debug("Running CLI with args %r", sys.argv)
        args.func(args)
