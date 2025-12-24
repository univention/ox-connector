# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Shared fixtures for unit tests.

These fixtures provide mock objects and patch external dependencies
to allow testing the provisioning logic in isolation.
"""

import sys
from unittest.mock import MagicMock

import pytest

from univention.ox.provisioning.models import TriggerObject


@pytest.fixture
def trigger_object():
    """
    Factory fixture to create TriggerObject instances for testing.

    Uses the actual TriggerObject class from univention.ox.provisioning.models.
    Allows setting old_attributes to None to simulate objects without old state
    (like FakeObject or newly created objects).
    """

    def _create(
        attributes=None,
        old_attributes=None,
        distinguished_name="cn=test,dc=example,dc=test",
        object_type="groups/group",
        entry_uuid="test-uuid",
        set_old_attributes=True,
        set_attributes=True,
    ):
        obj = TriggerObject(
            entry_uuid=entry_uuid,
            object_type=object_type,
            distinguished_name=distinguished_name,
            attributes=attributes or {},
            options=["default"],
            path=None,
        )
        # Mark old as loaded so was_added/was_modified/was_deleted work
        obj._old_loaded = True

        if set_old_attributes:
            obj.old_attributes = old_attributes or {}
            obj.old_distinguished_name = distinguished_name
        else:
            # Simulate object without old_attributes (like FakeObject)
            # by deleting the attribute entirely
            del obj.old_attributes

        if not set_attributes:
            # Simulate object without attributes (deletion scenario)
            del obj.attributes

        return obj

    return _create


@pytest.fixture
def mock_provisioning_object(trigger_object):
    """Alias for trigger_object fixture for backward compatibility."""
    return trigger_object


@pytest.fixture
def mock_user_object():
    """
    Factory fixture to create mock user objects returned by get_old_obj.

    Uses the actual TriggerObject class to be consistent.
    """

    def _create_user(context_id, username="testuser"):
        obj = TriggerObject(
            entry_uuid="user-uuid",
            object_type="users/user",
            distinguished_name=f"uid={username},dc=example,dc=test",
            attributes={
                "oxContext": context_id,
                "username": username,
                "isOxUser": "OK",
            },
            options=["default"],
            path=None,
        )
        obj._old_loaded = True
        return obj

    return _create_user


@pytest.fixture
def patch_helpers(mocker):
    """
    Patch the helpers module functions used by get_group_objs and get_account_objs.

    Returns a dict with the mock objects for further configuration in tests.
    """
    # Patch get_old_obj - by default returns None (user not found)
    mock_get_old_obj = mocker.patch(
        "univention.ox.provisioning.helpers.get_old_obj",
        return_value=None,
    )

    # Patch get_context_id - extracts oxContext from attributes
    def _get_context_id(attributes):
        from univention.ox.provisioning.helpers import Skip

        context_id = attributes.get("oxContext")
        if context_id is None:
            raise Skip("Object has no oxContext attribute!")
        return context_id

    mock_get_context_id = mocker.patch(
        "univention.ox.provisioning.get_context_id",
        side_effect=_get_context_id,
    )

    # Patch is_ox_group - checks isOxGroup attribute
    def _is_ox_group(attr):
        value = attr.get("isOxGroup")
        return value in {"OK", True}

    mock_is_ox_group = mocker.patch(
        "univention.ox.provisioning.is_ox_group",
        side_effect=_is_ox_group,
    )

    return {
        "get_old_obj": mock_get_old_obj,
        "get_context_id": mock_get_context_id,
        "is_ox_group": mock_is_ox_group,
    }


@pytest.fixture
def fake_object(mocker):
    """
    Factory fixture that provides the actual FakeObject class from consumer.py.

    The consumer module has many dependencies that need to be mocked before
    importing FakeObject.
    """
    # Mock the heavy dependencies before importing consumer
    mocker.patch.dict(
        sys.modules,
        {
            'univention.provisioning.consumer.api': MagicMock(),
            'univention.provisioning.models.message': MagicMock(),
            'config': MagicMock(),
            'univention.ox.provisioning.models': MagicMock(),
            'univention.ox.provisioning.contexts': MagicMock(),
            'univention.ox.provisioning.key_value_store': MagicMock(),
            'univention.ox.provisioning.users': MagicMock(),
        },
    )

    # Now we can import FakeObject from the actual consumer module
    from consumer import FakeObject

    return FakeObject
