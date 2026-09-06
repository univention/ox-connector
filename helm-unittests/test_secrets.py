# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.secret import SecretPasswords
import pytest


class TestProvisioningSecret(SecretPasswords):
    template_file = "templates/secret-provisioning-api.yaml"

    def values(self, localpart: dict) -> dict:
        return {"provisioningApi": localpart}

    @pytest.mark.skip(reason="Password is auto-generated")
    def test_auth_plain_values_password_is_required():
        pass

    @pytest.mark.skip(reason="Password in auto-generated")
    def test_global_secrets_keep_is_ignored():
        pass


class TestOxMasterPasswordSecret(SecretPasswords):
    template_file = "templates/secret-ox-master-password.yaml"

    def values(self, localpart: dict) -> dict:
        return {"openXchange": localpart}


class TestDbConnectionStringSecret(SecretPasswords):
    """The connection URL is the credential of this Secret.

    The harness drives `auth.password` and `auth.existingSecret`; they map onto
    `openXchange.oxDbConnectionString` and `openXchange.database.existingSecret`.
    """

    template_file = "templates/secret-db-connection-string.yaml"
    secret_key = "OX_CONNECTOR_DB"

    def values(self, localpart: dict) -> dict:
        auth = localpart.get("auth", {})
        open_xchange = {}
        if "password" in auth:
            open_xchange["oxDbConnectionString"] = auth["password"]
        if "existingSecret" in auth:
            existing_secret = dict(auth["existingSecret"])
            key_mapping = existing_secret.pop("keyMapping", None)
            if key_mapping is not None:
                existing_secret["keyMapping"] = {
                    "OX_CONNECTOR_DB": key_mapping.get("password"),
                }
            open_xchange["database"] = {"existingSecret": existing_secret}
        return {"openXchange": open_xchange}
