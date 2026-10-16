# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import subprocess

import pytest
from pytest_helm.utils import load_yaml
from univention.testing.helm.secret import SecretPasswords


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
    """
    Customized secret password tests for the DB connection string.

    These are mostly copy-pasted from the base class, necessary because this
    secret doesn't quite use the same structure (the plain value is
    `oxDbConnectionString` rather than `database.password`).
    """

    template_file = "templates/secret-db-connection-string.yaml"
    secret_key = "OX_CONNECTOR_DB"

    def values(self, localpart: dict) -> dict:
        return {"openXchange": localpart}

    def test_auth_plain_values_generate_secret(self, helm, chart_path):
        values = self.values(
            load_yaml('oxDbConnectionString: "stub-password"'),
        )
        result = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        assert (
            result.findone(f"stringData.{self.secret_key}") == "stub-password"
        )

    def test_auth_plain_values_password_is_not_templated(
        self,
        helm,
        chart_path,
    ):
        values = self.values(
            load_yaml('oxDbConnectionString: "{{ value }}"'),
        )
        result = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        assert result.findone(f"stringData.{self.secret_key}") == "{{ value }}"

    def test_auth_plain_values_password_is_required(self, helm, chart_path):
        values = self.values(
            load_yaml("oxDbConnectionString: null"),
        )
        with pytest.raises(subprocess.CalledProcessError):
            self.helm_template_file(
                helm,
                chart_path,
                values,
                self.template_file,
            )

    def test_auth_plain_values_password_has_no_default_value(
        self,
        helm,
        chart_path,
    ):
        values = {}
        helm.values = []

        with pytest.raises(subprocess.CalledProcessError):
            self.helm_template_file(
                helm,
                chart_path,
                values,
                self.template_file,
            )

    def test_auth_existing_secret_does_not_generate_a_secret(
        self,
        helm,
        chart_path,
    ):
        values = self.values(
            load_yaml(
                """
                database:
                  existingSecret:
                    name: "stub-secret-name"
                """,
            ),
        )
        result = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        assert result == {}

    def test_auth_existing_secret_does_not_require_plain_password(
        self,
        helm,
        chart_path,
    ):
        values = self.values(
            load_yaml(
                """
                oxDbConnectionString: null
                database:
                  existingSecret:
                    name: "stub-secret-name"
                """,
            ),
        )
        result = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        assert result == {}

    def test_auth_existing_secret_has_precedence(self, helm, chart_path):
        values = self.values(
            load_yaml(
                """
                oxDbConnectionString: "stub-plain-password"
                database:
                  existingSecret:
                    name: "stub-secret-name"
                """,
            ),
        )
        result = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        assert result == {}
