# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Unit tests for univention.ox.provisioning.users.set_mail_address_personal.
"""


from univention.ox.provisioning.users import set_mail_address_personal


def _user(mocker, user_id=42, context_id=1):
    """A minimal user double exposing id, context_id and service()."""
    return mocker.Mock(id=user_id, context_id=context_id)


def _obj(mocker, **attributes):
    """A minimal provisioning object double carrying attributes."""
    return mocker.Mock(attributes=dict(attributes))


def _soap_call(user):
    """The SOAP method the function is expected to invoke."""
    return user.service.return_value.change_mail_address_personal


class TestSetMailAddressPersonal:
    """Tests for the set_mail_address_personal function."""

    def test_uses_ox_display_name(self, mocker):
        """oxDisplayName is pushed to the primary account's personal."""
        user = _user(mocker)
        obj = _obj(mocker, oxDisplayName="Beta, Bruno (Referat 3B)")

        set_mail_address_personal(user, obj)

        user.service.assert_called_once_with(1)
        _soap_call(user).assert_called_once_with(
            {"id": 42},
            "Beta, Bruno (Referat 3B)",
        )

    def test_falls_back_to_display_name(self, mocker):
        """Without oxDisplayName the generic displayName is used."""
        user = _user(mocker)
        obj = _obj(mocker, displayName="Bruno Beta")

        set_mail_address_personal(user, obj)

        _soap_call(user).assert_called_once_with({"id": 42}, "Bruno Beta")

    def test_prefers_ox_display_name(self, mocker):
        """oxDisplayName wins when both attributes are present."""
        user = _user(mocker)
        obj = _obj(
            mocker,
            oxDisplayName="Beta, Bruno (Referat 3B)",
            displayName="Bruno Beta",
        )

        set_mail_address_personal(user, obj)

        _soap_call(user).assert_called_once_with(
            {"id": 42},
            "Beta, Bruno (Referat 3B)",
        )

    def test_unwraps_single_valued_lists(self, mocker):
        """LDAP style multi-values are reduced to their first entry."""
        user = _user(mocker)
        obj = _obj(mocker, oxDisplayName=["Beta, Bruno"])

        set_mail_address_personal(user, obj)

        _soap_call(user).assert_called_once_with({"id": 42}, "Beta, Bruno")

    def test_does_nothing_without_a_name(self, mocker):
        """No usable display name leaves the account untouched."""
        user = _user(mocker)

        set_mail_address_personal(user, _obj(mocker))
        set_mail_address_personal(user, _obj(mocker, oxDisplayName=""))
        set_mail_address_personal(user, _obj(mocker, oxDisplayName=[]))

        user.service.assert_not_called()

    def test_soap_errors_do_not_abort_provisioning(self, mocker):
        """A failing SOAP call is logged, not raised."""
        user = _user(mocker)
        _soap_call(user).side_effect = RuntimeError("SOAP down")

        set_mail_address_personal(
            user,
            _obj(mocker, oxDisplayName="Beta, Bruno"),
        )
