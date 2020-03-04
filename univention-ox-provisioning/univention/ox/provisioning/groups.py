import logging

from univention.ox.backend_base import get_ox_integration_class
from univention.ox.provisioning import get_context_id
from univention.ox.provisioning.users import get_user_id


Group = get_ox_integration_class("SOAP", "Group")
logger = logging.getLogger("listener")


def group_from_attributes(attributes, group_id=None):
    group = Group(id=group_id)
    if attributes:
        context_id = attributes["oxContext"]
        group.context_id = context_id
        update_group(group, attributes)
    return group


def update_group(group, attributes):
    group.name = attributes.get("name")
    group.display_name = group.name
    if attributes.get("isOxGroup", "Not") == "Not":
        # no need to search anything...
        # specifically skip "Domain Users"... this would be expensive
        return
    members = []
    logger.info("Retrieving members...")
    for user in attributes.get("users"):
        username = user[4:].split(",")[0]  # TODO: make this more elegant
        user_attributes = {}
        user_attributes["oxContext"] = get_context_id(attributes)
        user_attributes["username"] = username
        user_id = get_user_id(user_attributes)
        if user_id:
            logger.info(f"... found {user_id}")
            members.append(user_id)
    group.members = members


def get_group_id(obj):
    if obj.old_attributes is not None:
        # before delete
        context_id = obj.old_attributes["oxContext"]
        groupname = obj.old_attributes.get("name")
    else:
        # before create
        context_id = obj.attributes["oxContext"]
        groupname = obj.attributes.get("name")
    # ignore groups with name "users" (Bug #35821)
    if groupname.lower() == "users":
        logger.info(f'Ignoring group "{groupname}"')
        return None
    groups = Group.list(context_id, pattern=groupname)
    if not groups:
        return None
    assert len(groups) == 1
    return groups[0].id


def create_group(obj):
    logger.info(f"Creating {obj}")
    if obj.attributes.get("isOxGroup", "Not") == "Not":
        logger.info(f"{obj} is no OX group. Deleting instead...")
        return delete_group(obj)
    if get_group_id(obj):
        logger.info(f"{obj} exists. Modifying instead...")
        return modify_group(obj)
    group = group_from_attributes(obj.attributes)
    if not group.members:
        logger.info(f"{obj} is empty. Deleting instead...")
        return delete_group(obj)
    # ignore groups with name "users" (Bug #35821)
    if group.name == "users":
        return
    group.create()


def modify_group(obj):
    logger.info(f"Modifying {obj}")
    if obj.attributes.get("isOxGroup", "Not") == "Not":
        logger.info(f"{obj} is no OX group. Deleting instead...")
        return delete_group(obj)
    group_id = get_group_id(obj)
    if not group_id:
        logger.info(f"{obj} does not yet exist. Creating instead...")
        return create_group(obj)
    if obj.old_attributes:
        if obj.old_attributes.get("isOxGroup", "Not") == "Not":
            logger.info(
                f"{obj} was no OX group before... that should not be the case. Modifying anyway..."
            )
        group = group_from_attributes(obj.old_attributes, group_id)
        update_group(group, obj.attributes)
    else:
        logger.info(f"{obj} has no old data. Resync?")
        group = group_from_attributes(obj.attributes, group_id)
    if not group.members:
        logger.info(f"{obj} is empty. Deleting instead...")
        return delete_group(obj)
    group.modify()


def delete_group(obj):
    logger.info(f"Deleting {obj}")
    group_id = get_group_id(obj)
    if not group_id:
        logger.info(f"{obj} does not exist. Doing nothing...")
        return
    group = group_from_attributes(obj.old_attributes, group_id)
    group.remove()
    obj.attributes = None  # make obj.was_deleted() return True
