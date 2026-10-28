# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH


from unittest.mock import Mock

import pytest
from univention.ox.provisioning.users import set_mail_address_personal


class TestSetMailAddressPersonal:
    """Tests for the set_mail_address_personal function."""

    def _assert_soap_call(self, user, personal):
        user.service.assert_called_once_with(user.context_id)
        soap_function = user.service.return_value.change_mail_address_personal
        soap_function.assert_called_once_with(
            {"id": user.id},
            personal,
        )

    def _assert_no_soap_call(self, user):
        user.service.assert_not_called()

    def test_sets_personal_to_display_name(self):
        user = Mock(display_name="expected")
        self._assert_no_soap_call(user)
        set_mail_address_personal(user)
        self._assert_soap_call(user, "expected")

    @pytest.mark.parametrize("value", ["", None])
    def test_doesnt_use_empty_display_name(self, value):
        user = Mock(display_name=value)
        set_mail_address_personal(user)
        self._assert_no_soap_call(user)

    def test_drops_soap_errors(self):
        user = Mock(display_name="expected")
        user.service.return_value.change_mail_address_personal.side_effect = (
            RuntimeError("SOAP down")
        )
        set_mail_address_personal(user)
