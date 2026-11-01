# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import os

import pytest

os.environ.setdefault("OX_CONNECTOR_DB", "sqlite://")

from univention.ox.provisioning.db import get_db_url  # noqa: E402


@pytest.mark.parametrize(
    "connection_string,expected_drivername",
    [
        ("postgresql://u:p@host:5432/db", "postgresql+psycopg2"),
        ("postgresql+psycopg2://u:p@host/db", "postgresql+psycopg2"),
        ("postgresql+psycopg://u:p@host/db", "postgresql+psycopg"),
        ("sqlite:////tmp/ox-connector.db", "sqlite"),
    ],
)
def test_get_db_url_driver(
    monkeypatch,
    connection_string,
    expected_drivername,
):
    monkeypatch.setenv("OX_CONNECTOR_DB", connection_string)
    url = get_db_url()
    assert url.drivername == expected_drivername


def test_get_db_url_keeps_credentials(monkeypatch):
    monkeypatch.setenv(
        "OX_CONNECTOR_DB",
        "postgresql://user:secret@host:5432/db",
    )
    url = get_db_url()
    assert (url.username, url.password, url.host, url.port, url.database) == (
        "user",
        "secret",
        "host",
        5432,
        "db",
    )
