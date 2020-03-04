import logging

from univention.ox.backend_base import get_ox_integration_class

Context = get_ox_integration_class("SOAP", "Context")
logger = logging.getLogger("listener")


def context_from_attributes(attributes):
    context = Context(id=attributes["contextid"])
    update_context(context, attributes)
    return context


def update_context(context, attributes):
    context.max_quota = attributes.get("oxQuota")
    context.name = attributes["name"]


def context_exists(obj):
    if obj.attributes is None:
        # before delete
        context_id = obj.old_attributes["contextid"]
    else:
        # before create
        context_id = obj.attributes["contextid"]
    return bool(Context.list(pattern=context_id))


def create_context(obj):
    logger.info(f"Creating {obj}")
    if context_exists(obj):
        logger.info(f"{obj} exists. Modifying instead...")
        return modify_context(obj)
    context = context_from_attributes(obj.attributes)
    context.create()


def modify_context(obj):
    logger.info(f"Modifying {obj}")
    if obj.old_attributes:
        context = context_from_attributes(obj.old_attributes)
        update_context(context, obj.attributes)
    else:
        logger.info(f"{obj} has no old data. Resync?")
        context = context_from_attributes(obj.attributes)
    context.modify()


def delete_context(obj):
    logger.info(f"Deleting {obj}")
    if not context_exists(obj):
        logger.info(f"{obj} does not exist. Doing nothing...")
        return
    context = context_from_attributes(obj.old_attributes)
    context.remove()
    obj.attributes = None  # make obj.was_deleted() return True
