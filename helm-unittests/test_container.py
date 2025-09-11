# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.container import ContainerEnvVarSecret
import pytest


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
