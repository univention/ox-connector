import logging
from copy import deepcopy

from univention.ox.backend_base import get_ox_integration_class
from univention.ox.provisioning import get_context_id

Resource = get_ox_integration_class("SOAP", "Resource")
logger = logging.getLogger("listener")


def resource_from_attributes(attributes, resource_id=None):
    context_id = get_context_id(attributes)
    resource = Resource(id=resource_id, context_id=context_id)
    update_resource(resource, attributes)
    return resource


def update_resource(resource, attributes):
    resource.name = attributes.get("name")
    resource.description = attributes.get("description")
    resource.display_name = attributes.get("displayname")
    resource.email = attributes.get("resourceMailAddress")


def get_resource_id(attributes):
    context_id = get_context_id(attributes)
    name = attributes.get("name")
    resources = Resource.list(context_id, pattern=name)
    if not resources:
        return None
    assert len(resources) == 1
    return resources[0].id


def create_resource(obj):
    logger.info(f"Creating {obj}")
    if get_resource_id(obj.attributes):
        logger.info(f"{obj} exists. Modifying instead...")
        return modify_resource(obj)
    resource = resource_from_attributes(obj.attributes)
    resource.create()


def modify_resource(obj):
    logger.info(f"Modifying {obj}")
    resource_id = get_resource_id(obj.old_attributes)
    if not resource_id:
        logger.info(f"{obj} does not yet exist. Creating instead...")
        return create_resource(obj)
    if obj.old_attributes:
        old_context = get_context_id(obj.old_attributes)
        new_context = get_context_id(obj.attributes)
        if old_context != new_context:
            logging.info(f"Changing context: {old_context} -> {new_context}")
            already_existing_resource_id = get_resource_id(obj.attributes)
            if already_existing_resource_id:
                logger.warning(
                    f"{obj} was found in context {old_context} with ID {resource_id} and in {new_context} with {already_existing_resource_id}. This should not happen. Will delete in {old_context} and modify in {new_context}"  # noqa
                )
                delete_resource(deepcopy(obj))
            else:
                create_resource(obj)
                return delete_resource(deepcopy(obj))
        resource = resource_from_attributes(obj.old_attributes, resource_id)
        update_resource(resource, obj.attributes)
    else:
        logger.info(f"{obj} has no old data. Resync?")
        resource = resource_from_attributes(obj.attributes, resource_id)
    resource.modify()


def delete_resource(obj):
    logger.info(f"Deleting {obj}")
    resource_id = get_resource_id(obj.old_attributes)
    if not resource_id:
        logger.info(f"{obj} does not exist. Doing nothing...")
        return
    resource = resource_from_attributes(obj.old_attributes, resource_id)
    resource.remove()
    obj.attributes = None  # make obj.was_deleted() return True
