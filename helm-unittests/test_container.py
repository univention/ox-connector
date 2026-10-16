# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from pytest_helm.utils import add_jsonpath_prefix, load_yaml
from univention.testing.helm.container import ContainerEnvVarSecret


@pytest.mark.parametrize(
    "key,env_var",
    [
        ("openXchange", "OX_MASTER_PASSWORD"),
        ("provisioningApi", "PROVISIONING_API_PASSWORD"),
    ],
)
class TestOxConnectorEnvVarSecrets(ContainerEnvVarSecret):
    template_file = "templates/statefulset.yaml"
    container_name = "main"


class BaseTestOxConnectorDbConnectionStringEnvVarSecrets(
    ContainerEnvVarSecret,
):
    """
    Custom base test for the DB connection string.

    These are essentially copy-pasted from ContainerEnvVarSecret, with minor
    adaptations to account for the fact that our plaintext password is in
    `oxDbConnectionString` rather than `auth.password`, the existing secret
    in `database.existingSecret` rather than `auth.existingSecret` and the env
    variable is called `OX_CONNECTOR_DB` rather than `password`.
    """

    template_file = "templates/statefulset.yaml"
    chart_name = "ox-connector"

    @pytest.fixture
    def key(self):
        return "openXchange"

    @pytest.fixture
    def env_var(self):
        return "OX_CONNECTOR_DB"

    def test_auth_existing_secret_custom_name(
        self,
        helm,
        chart_path,
        key,
        env_var,
    ):
        values = add_jsonpath_prefix(
            key,
            load_yaml(
                """
                database:
                  existingSecret:
                    name: "stub-secret-name"
            """,
            ),
        )
        container_type = (
            "initContainers" if self.container_is_init else "containers"
        )
        deployment = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        env = deployment.findone(
            f"spec.template.spec.{container_type}[?@.name=='{self.container_name}'].env[?@.name=='{env_var}']",
        )
        assert env["valueFrom"]["secretKeyRef"]["name"] == "stub-secret-name"
        assert env["valueFrom"]["secretKeyRef"]["key"] == "OX_CONNECTOR_DB"

    def test_auth_disabling_existing_secret(
        self,
        helm,
        chart_path,
        key,
        env_var,
    ):
        values = add_jsonpath_prefix(
            key,
            load_yaml(
                """
                database:
                  existingSecret: null
            """,
            ),
        )
        container_type = (
            "initContainers" if self.container_is_init else "containers"
        )
        deployment = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        env = deployment.findone(
            f"spec.template.spec.{container_type}[?@.name=='{self.container_name}'].env[?@.name=='{env_var}']",
        )
        assert env["valueFrom"]["secretKeyRef"]["name"].startswith(
            f"release-name-{self.chart_name}",
        ), f"Secret name {env['valueFrom']['secretKeyRef']['name']} does not start with release-name-{self.chart_name}"
        assert env["valueFrom"]["secretKeyRef"]["key"] == "OX_CONNECTOR_DB"

    def test_auth_existing_secret_custom_key(
        self,
        helm,
        chart_path,
        key,
        env_var,
    ):
        values = add_jsonpath_prefix(
            key,
            load_yaml(
                """
                database:
                  existingSecret:
                    name: "stub-secret-name"
                    keyMapping:
                      OX_CONNECTOR_DB: "stub_password_key"
            """,
            ),
        )
        container_type = (
            "initContainers" if self.container_is_init else "containers"
        )
        deployment = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        env = deployment.findone(
            f"spec.template.spec.{container_type}[?@.name=='{self.container_name}'].env[?@.name=='{env_var}']",
        )
        assert env["valueFrom"]["secretKeyRef"]["name"] == "stub-secret-name"
        assert env["valueFrom"]["secretKeyRef"]["key"] == "stub_password_key"

    def test_auth_existing_secret_has_precedence(
        self,
        helm,
        chart_path,
        key,
        env_var,
    ):
        values = add_jsonpath_prefix(
            key,
            load_yaml(
                """
                oxDbConnectionString: "stub-plain-password"
                database:
                  existingSecret:
                    name: "stub-secret-name"
                    keyMapping:
                      OX_CONNECTOR_DB: "stub_password_key"
            """,
            ),
        )
        container_type = (
            "initContainers" if self.container_is_init else "containers"
        )
        deployment = self.helm_template_file(
            helm,
            chart_path,
            values,
            self.template_file,
        )
        env = deployment.findone(
            f"spec.template.spec.{container_type}[?@.name=='{self.container_name}'].env[?@.name=='{env_var}']",
        )
        assert env["valueFrom"]["secretKeyRef"]["name"] == "stub-secret-name"
        assert env["valueFrom"]["secretKeyRef"]["key"] == "stub_password_key"


class TestOxConnectorDbConnectionStringInInitDbEnvVarSecrets(
    BaseTestOxConnectorDbConnectionStringEnvVarSecrets,
):
    container_name = "init-db"
    container_is_init = True


class TestOxConnectorDbConnectionStringInMainEnvVarSecrets(
    BaseTestOxConnectorDbConnectionStringEnvVarSecrets,
):
    container_name = "main"
    container_is_init = False
