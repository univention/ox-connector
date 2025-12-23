# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Unit tests for univention.ox.provisioning.__init__ module.
"""


from univention.ox.provisioning import get_group_objs, get_account_objs


class TestGetGroupObjs:
    """Tests for the get_group_objs function."""

    def test_returns_empty_when_not_ox_group(
        self,
        mock_provisioning_object,
        patch_helpers,
    ):
        """A group with isOxGroup=False should yield no objects."""
        obj = mock_provisioning_object(
            attributes={
                "name": "testgroup",
                "users": ["uid=user1,dc=example,dc=test"],
                "isOxGroup": False,
            },
            old_attributes={
                "name": "testgroup",
                "users": ["uid=user1,dc=example,dc=test"],
                "isOxGroup": False,
            },
        )

        result = list(get_group_objs(obj))

        assert result == []

    def test_with_both_attributes(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Group with both attributes and old_attributes should work correctly."""
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        obj = mock_provisioning_object(
            attributes={
                "name": "testgroup",
                "users": [user_dn],
                "isOxGroup": True,
            },
            old_attributes={
                "name": "testgroup",
                "users": [user_dn],
                "isOxGroup": True,
            },
        )

        result = list(get_group_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id
        assert result[0].old_attributes["oxContext"] == context_id

    def test_missing_old_attributes(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """
        Object missing old_attributes should not raise AttributeError.
        """
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        # Create object WITHOUT old_attributes
        obj = mock_provisioning_object(
            attributes={
                "name": "testgroup",
                "users": [user_dn],
                "isOxGroup": True,
            },
            set_old_attributes=False,  # Don't set old_attributes at all
        )

        # This should NOT raise AttributeError
        result = list(get_group_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id
        # The result object should also not have old_attributes
        assert not hasattr(result[0], "old_attributes")

    def test_missing_attributes(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """
        Object missing attributes (only old_attributes) should not raise AttributeError.
        """
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        # Create object WITHOUT attributes (deletion scenario)
        obj = mock_provisioning_object(
            old_attributes={
                "name": "testgroup",
                "users": [user_dn],
                "isOxGroup": True,
            },
            set_attributes=False,
        )

        result = list(get_group_objs(obj))

        assert len(result) == 1
        assert result[0].old_attributes["oxContext"] == context_id
        assert not hasattr(result[0], "attributes")

    def test_missing_both_attributes(
        self,
        mock_provisioning_object,
        patch_helpers,
    ):
        """Object missing both attributes should yield no results (ignored group)."""
        obj = mock_provisioning_object(
            set_attributes=False,
            set_old_attributes=False,
        )

        result = list(get_group_objs(obj))

        assert result == []

    def test_multiple_users_same_context(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Multiple users in the same context should result in one group object."""
        user_dn1 = "uid=user1,dc=example,dc=test"
        user_dn2 = "uid=user2,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        obj = mock_provisioning_object(
            attributes={
                "name": "testgroup",
                "users": [user_dn1, user_dn2],
                "isOxGroup": True,
            },
            old_attributes={
                "name": "testgroup",
                "users": [user_dn1, user_dn2],
                "isOxGroup": True,
            },
        )

        result = list(get_group_objs(obj))

        assert len(result) == 1
        assert len(result[0].attributes["users"]) == 2

    def test_multiple_users_different_contexts(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Users in different contexts should yield multiple group objects."""
        user_dn1 = "uid=user1,dc=example,dc=test"
        user_dn2 = "uid=user2,dc=example,dc=test"
        context_id1 = 10
        context_id2 = 20

        # Return different contexts based on which user is looked up
        def get_old_obj_side_effect(dn):
            if dn == user_dn1:
                return mock_user_object(context_id1, "user1")
            elif dn == user_dn2:
                return mock_user_object(context_id2, "user2")
            return None

        patch_helpers["get_old_obj"].side_effect = get_old_obj_side_effect

        obj = mock_provisioning_object(
            attributes={
                "name": "testgroup",
                "users": [user_dn1, user_dn2],
                "isOxGroup": True,
            },
            old_attributes={
                "name": "testgroup",
                "users": [user_dn1, user_dn2],
                "isOxGroup": True,
            },
        )

        result = list(get_group_objs(obj))

        assert len(result) == 2
        contexts = {r.attributes["oxContext"] for r in result}
        assert contexts == {context_id1, context_id2}

    def test_unknown_user_is_ignored(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Users not found by get_old_obj should be ignored."""
        user_dn1 = "uid=user1,dc=example,dc=test"
        user_dn2 = "uid=unknown,dc=example,dc=test"
        context_id = 10

        def get_old_obj_side_effect(dn):
            if dn == user_dn1:
                return mock_user_object(context_id, "user1")
            return None  # Unknown user

        patch_helpers["get_old_obj"].side_effect = get_old_obj_side_effect

        obj = mock_provisioning_object(
            attributes={
                "name": "testgroup",
                "users": [user_dn1, user_dn2],
                "isOxGroup": True,
            },
            old_attributes={
                "name": "testgroup",
                "users": [user_dn1, user_dn2],
                "isOxGroup": True,
            },
        )

        result = list(get_group_objs(obj))

        assert len(result) == 1
        # Only user1 should be in the group
        assert len(result[0].attributes["users"]) == 1


class TestGetAccountObjs:
    """Tests for the get_account_objs function."""

    def test_with_both_attributes(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Account with both attributes and old_attributes should work correctly."""
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        obj = mock_provisioning_object(
            attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [],
            },
            old_attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [],
            },
        )

        result = list(get_account_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id
        assert result[0].old_attributes["oxContext"] == context_id

    def test_missing_old_attributes(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """
        Account missing old_attributes should not raise AttributeError.

        This is the main bug fix scenario from commit ffb7c17.
        """
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        obj = mock_provisioning_object(
            attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [],
            },
            set_old_attributes=False,
        )

        # This should NOT raise AttributeError
        result = list(get_account_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id
        assert not hasattr(result[0], "old_attributes")

    def test_missing_attributes(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Account missing attributes should not raise AttributeError."""
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        obj = mock_provisioning_object(
            old_attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [],
            },
            set_attributes=False,
        )

        result = list(get_account_objs(obj))

        assert len(result) == 1
        assert result[0].old_attributes["oxContext"] == context_id
        assert not hasattr(result[0], "attributes")

    def test_missing_both_attributes(
        self,
        mock_provisioning_object,
        patch_helpers,
    ):
        """Account missing both attributes should yield no results."""
        obj = mock_provisioning_object(
            set_attributes=False,
            set_old_attributes=False,
        )

        result = list(get_account_objs(obj))

        assert result == []

    def test_multiple_users_same_context(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Multiple users in same context should result in one account object."""
        user_dn1 = "uid=user1,dc=example,dc=test"
        user_dn2 = "uid=user2,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        obj = mock_provisioning_object(
            attributes={
                "name": "testaccount",
                "users": [user_dn1, user_dn2],
                "groups": [],
            },
            old_attributes={
                "name": "testaccount",
                "users": [user_dn1, user_dn2],
                "groups": [],
            },
        )

        result = list(get_account_objs(obj))

        assert len(result) == 1
        assert len(result[0].attributes["users"]) == 2

    def test_multiple_users_different_contexts(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
    ):
        """Users in different contexts should yield multiple account objects."""
        user_dn1 = "uid=user1,dc=example,dc=test"
        user_dn2 = "uid=user2,dc=example,dc=test"
        context_id1 = 10
        context_id2 = 20

        def get_old_obj_side_effect(dn):
            if dn == user_dn1:
                return mock_user_object(context_id1, "user1")
            elif dn == user_dn2:
                return mock_user_object(context_id2, "user2")
            return None

        patch_helpers["get_old_obj"].side_effect = get_old_obj_side_effect

        obj = mock_provisioning_object(
            attributes={
                "name": "testaccount",
                "users": [user_dn1, user_dn2],
                "groups": [],
            },
            old_attributes={
                "name": "testaccount",
                "users": [user_dn1, user_dn2],
                "groups": [],
            },
        )

        result = list(get_account_objs(obj))

        assert len(result) == 2
        contexts = {r.attributes["oxContext"] for r in result}
        assert contexts == {context_id1, context_id2}

    def test_with_groups(
        self,
        mock_provisioning_object,
        mock_user_object,
        patch_helpers,
        mocker,
    ):
        """Account with groups should process group members."""
        user_dn = "uid=user1,dc=example,dc=test"
        group_dn = "cn=group1,dc=example,dc=test"
        context_id = 10

        # Create a mock group object that get_group_objs will process
        mock_group = mock_provisioning_object(
            attributes={
                "name": "group1",
                "users": [user_dn],
                "isOxGroup": True,
                "oxContext": context_id,
            },
            old_attributes={
                "name": "group1",
                "users": [user_dn],
                "isOxGroup": True,
            },
        )

        def get_old_obj_side_effect(dn):
            if dn == user_dn:
                return mock_user_object(context_id, "user1")
            elif dn == group_dn:
                return mock_group
            return None

        patch_helpers["get_old_obj"].side_effect = get_old_obj_side_effect

        obj = mock_provisioning_object(
            attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [group_dn],
            },
            old_attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [group_dn],
            },
        )

        result = list(get_account_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id
        # Group should be in the groups list
        assert group_dn in result[0].attributes["groups"]


class TestWithFakeObject:
    """
    Tests using the actual FakeObject class from standalone-files/consumer.py.
    """

    def test_get_group_objs_with_fake_object(
        self,
        fake_object,
        mock_user_object,
        patch_helpers,
    ):
        """
        get_group_objs should handle FakeObject which only has attributes.

        FakeObject is used by the standalone consumer to represent cached
        objects that only have attributes (no old_attributes).
        """
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        # FakeObject only has attributes, no old_attributes
        obj = fake_object(
            {
                "name": "testgroup",
                "users": [user_dn],
                "isOxGroup": True,
            },
        )

        # This should NOT raise AttributeError
        result = list(get_group_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id

    def test_get_account_objs_with_fake_object(
        self,
        fake_object,
        mock_user_object,
        patch_helpers,
    ):
        """
        get_account_objs should handle FakeObject which only has attributes.

        FakeObject is used by the standalone consumer to represent cached
        objects that only have attributes (no old_attributes).
        """
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        patch_helpers["get_old_obj"].return_value = mock_user_object(
            context_id,
        )

        # FakeObject only has attributes, no old_attributes
        obj = fake_object(
            {
                "name": "testaccount",
                "users": [user_dn],
                "groups": [],
            },
        )

        # This should NOT raise AttributeError
        result = list(get_account_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id

    def test_get_group_objs_with_fake_object_as_user_lookup_result(
        self,
        fake_object,
        mock_provisioning_object,
        patch_helpers,
    ):
        """
        get_group_objs should work when get_old_obj returns a FakeObject.

        This tests the scenario where get_old_obj (overwritten in consumer.py)
        returns a FakeObject for user lookups.
        """
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        # get_old_obj returns FakeObject (as in consumer.py)
        fake_user = fake_object(
            {
                "oxContext": context_id,
                "oxDbId": 123,
                "username": "user1",
            },
        )
        patch_helpers["get_old_obj"].return_value = fake_user

        obj = mock_provisioning_object(
            attributes={
                "name": "testgroup",
                "users": [user_dn],
                "isOxGroup": True,
            },
            old_attributes={
                "name": "testgroup",
                "users": [user_dn],
                "isOxGroup": True,
            },
        )

        result = list(get_group_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id

    def test_get_account_objs_with_fake_object_as_user_lookup_result(
        self,
        fake_object,
        mock_provisioning_object,
        patch_helpers,
    ):
        """
        get_account_objs should work when get_old_obj returns a FakeObject.

        This tests the scenario where get_old_obj (overwritten in consumer.py)
        returns a FakeObject for user lookups.
        """
        user_dn = "uid=user1,dc=example,dc=test"
        context_id = 10

        # get_old_obj returns FakeObject (as in consumer.py)
        fake_user = fake_object(
            {
                "oxContext": context_id,
                "oxDbId": 123,
                "username": "user1",
            },
        )
        patch_helpers["get_old_obj"].return_value = fake_user

        obj = mock_provisioning_object(
            attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [],
            },
            old_attributes={
                "name": "testaccount",
                "users": [user_dn],
                "groups": [],
            },
        )

        result = list(get_account_objs(obj))

        assert len(result) == 1
        assert result[0].attributes["oxContext"] == context_id
