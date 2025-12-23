# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Shared fixtures for unit tests.

These fixtures provide mock objects and patch external dependencies
to allow testing the provisioning logic in isolation.
"""

import sys
from copy import deepcopy
from unittest.mock import MagicMock

import pytest


class MockProvisioningObject:
    """
    A mock object that simulates the provisioning objects passed to
    get_group_objs and get_account_objs.
    """

    def __init__(
        self,
        attributes=None,
        old_attributes=None,
        distinguished_name="cn=test,dc=example,dc=test",
        set_attributes=True,
        set_old_attributes=True,
    ):
        self.distinguished_name = distinguished_name

        # Only set attributes if explicitly requested
        # This allows testing getattr() defensive behavior
        if set_attributes and attributes is not None:
            self.attributes = attributes
        elif set_attributes:
            self.attributes = {}

        if set_old_attributes and old_attributes is not None:
            self.old_attributes = old_attributes
        elif set_old_attributes:
            self.old_attributes = {}

    def __deepcopy__(self, memo):
        """Support deepcopy for the object splitting logic."""
        new_obj = MockProvisioningObject.__new__(MockProvisioningObject)
        new_obj.distinguished_name = self.distinguished_name

        if hasattr(self, "attributes"):
            new_obj.attributes = deepcopy(self.attributes, memo)
        if hasattr(self, "old_attributes"):
            new_obj.old_attributes = deepcopy(self.old_attributes, memo)

        return new_obj

    def __repr__(self):
        return f"MockProvisioningObject(dn={self.distinguished_name})"


@pytest.fixture
def mock_provisioning_object():
    """Factory fixture to create mock provisioning objects."""
    return MockProvisioningObject


@pytest.fixture
def mock_user_object():
    """Factory fixture to create mock user objects returned by get_old_obj."""

    def _create_user(context_id, username="testuser"):
        user = MagicMock()
        user.attributes = {
            "oxContext": context_id,
            "username": username,
            "isOxUser": "OK",
        }
        return user

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
