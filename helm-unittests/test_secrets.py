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
