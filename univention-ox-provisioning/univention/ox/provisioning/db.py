import pprint
import json
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, insert, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("postgresql+psycopg2://ox-connector:8cdcc28f11751636d14b2e395014a4bc4de14017ca1c3966b0f12c83a8e5af6b@localhost:5432/ox-connector")

class Dead(Base):
    __tablename__ = "rejected_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)
    error_msg = Column(String, nullable=False)

class Old(Base):
    __tablename__ = "old_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    obj_id = Column(String, nullable=False)
    udm_module = Column(String, nullable=False)
    dn = Column(String, nullable=False)
    attrs = Column(String, nullable=False)
    status = Column(String, nullable=False, default="new")
    num_errors = Column(Integer, nullable=False, default=0)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)


def add_task(path: Path):
    """
    Adds the content of a JSON file to the queue of tasks
    """
    with path.open() as file_handler:
        content = json.load(file_handler)
    udm_module = content["udm_object_type"]
    dn = content["dn"]
    attrs = content["object"]
    obj_id = attrs.get("univentionObjectIdentifier", "")
    with Session() as db_session:
        task = Task(obj_id=obj_id, udm_module=udm_module, dn=dn, attrs=json.dumps(attrs))
        db_session.add(task)
        db_session.commit()


def add_old(path: Path):
    """
    Adds the content of a JSON file to the database of already seen objects
    ("old db")
    """
    with path.open() as file_handler:
        content = json.load(file_handler)
    udm_module = content["udm_object_type"]
    dn = content["dn"]
    attrs = content["object"]
    obj_id = attrs.get("univentionObjectIdentifier", "")
    with Session() as db_session:
        old = db_session.query(Old).filter_by(obj_id=obj_id).first()
        if old:
            old.obj_id = obj_id
            old.udm_module = udm_module
            old.dn = dn
            old.attrs = json.dumps(attrs)
        else:
            old = Old(obj_id=obj_id, udm_module=udm_module, dn=dn, attrs=json.dumps(attrs))
        db_session.add(old)
        db_session.commit()


def move_task_to_dead_letters(task_id: int, error_msg: str):
    """
    Move the task to the "dead queue", meaning that it needs further, manual
    investigation. Removed from the list of active tasks.
    """
    with Session() as db_session:
        task = db_session.query(Task).get(task_id)
        dead = Dead(obj_id=task.obj_id, udm_module=task.udm_module, dn=task.dn, attrs=task.attrs, error_msg=error_msg)
        db_session.add(dead)
        db_session.delete(task)
        db_session.commit()


def move_task_to_old(task_id: int):
    """
    Move the task to the "old database", meaning that this data is now
    considered the last snapshot for further updates of this object. Removed
    from the list of active tasks.
    """
    with Session() as db_session:
        task = db_session.query(Task).get(task_id)
        old = db_session.query(Old).filter_by(obj_id=task.obj_id).first()
        if old:
            old.obj_id = task.obj_id
            old.udm_module = task.udm_module
            old.dn = task.dn
            old.attrs = task.attrs
        else:
            old = Old(obj_id=task.obj_id, udm_module=task.udm_module, dn=task.dn, attrs=task.attrs)
        db_session.add(old)
        for error in filter_error(task.obj_id, print_json=False):
            db_session.delete(error)
        db_session.delete(task)
        db_session.commit()


def filter_error(obj_id, print_json: bool=True, retry: bool=False, fresh_resync: bool=False, delete: bool=False):
    """
    Filter in the "dead queue". Objects found can be printed, retried (the
    exact same data are moved to the list of active tasks), fresh resync (this
    object is freshly added from the leading database to the list of active
    tasks), delete (error is deleted; makes sense to combine this with retry or
            resync)
    """
    with Session() as db_session:
        errors = error in db_session.query(Dead).where(Dead.obj_id.like(obj_id)).all()
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
                raise NotImplementedError()
            if delete:
                db_session.delete(error)
        db_session.commit()
        return errors


def _call(func, args):
    from copy import deepcopy
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


if __name__ == "__main__":
    from argparse import ArgumentParser

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
        args.func(args)
