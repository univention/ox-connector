#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import json
import logging

from configurator import RemoteConfigurator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class SSHConfigurator(RemoteConfigurator):
    def __init__(
        self,
        host=None,
        port=22,
        user="root",
        password="",
        timeout=300,
        sync_files=False,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.sync_files = sync_files
        self.files = {}
        self.services = []

    def _get_files(self) -> dict[str, str]:
        return {
            "/var/lib/univention-appcenter/apps/ox-connector/data/secrets/contexts.json": "/tmp/contexts.json",
            "/var/lib/univention-appcenter/apps/ox-connector/data/listener/ox-connector.db": "/var/lib/univention-appcenter/apps/ox-connector/data/listener/ox-connector.db",
        }

    def __enter__(self):
        if not self.sync_files:
            return self

        with self._connect() as ssh_client:
            self.files = self._get_files()

            with ssh_client.get_transport().open_sftp_client() as sftp:
                for remote, local in self.files.items():
                    logger.info(f"Download remote file: {remote} -> {local}")
                    try:
                        sftp.get(remote, local)
                    except FileNotFoundError:
                        logger.info("File not found")
                        pass

            self.services = [
                "docker-app-ox-connector.service",
                "univention-appcenter-listener-converter@ox-connector.service",
            ]
            for service in self.services:
                logger.info(f"Stopping service {service}")
                self._run(ssh_client, f"systemctl stop {service}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self.files) == 0 and len(self.services) == 0:
            return

        with self._connect() as ssh_client:
            with ssh_client.get_transport().open_sftp_client() as sftp:
                for remote, local in self.files.items():
                    logger.info(f"Upload local file: {local} -> {remote}")
                    try:
                        sftp.put(local, remote)
                    except FileNotFoundError:
                        logger.info("File not found")
                        pass

            for service in self.services:
                logger.info(f"Starting service {service}")
                self._run(ssh_client, f"systemctl start {service}")

    def _connect(self):
        from paramiko import SSHClient, AutoAddPolicy

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(
            hostname=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            look_for_keys=False,
        )

        return self.client

    def _run(self, ssh_client, command: str) -> str:
        _, stdout, stderr = ssh_client.exec_command(
            command,
            timeout=self.timeout,
        )
        stdout.channel.recv_exit_status()

        output = stdout.read().decode(
            'utf-8',
            errors='replace',
        ) + stderr.read().decode('utf-8', errors='replace')
        if stdout.channel.exit_status != 0:
            raise Exception(
                f"Comand returned with error {stdout.channel.exit_status}: {output}",
            )

        return output

    def get_configurations(self) -> dict:
        logger.info(f"Fetching configurations from {self.host}")
        python_code = """from univention.config_registry import ConfigRegistry
from dotenv import dotenv_values
from urllib.parse import urlparse, urlunparse

import sys
import json
import ipaddress
import socket
from pathlib import Path

ucr = ConfigRegistry()
ucr.load()
configs = {}

def to_ip(input: str) -> str | None:
    if input is None:
        return None

    try:
        address = ipaddress.ip_address(input)
        return str(address)
    except ValueError:
        pass

    return socket.gethostbyname(input)

ucr_mappings = {
    "provisioning-service/primary": {
        "name": "provisioning_api_host",
        "transform_cb": to_ip
    },
    "appcenter/apps/provisioning-service/ports/7777": {
        "name": "provisioning_api_port"
    },
    "domainname": {
        "name": "domain_name"
    },
    "ldap/server/name": {
        "name": "ldap_server",
        "transform_cb": to_ip
    },
    "ldap/server/port": {
        "name": "ldap_port"
    },
    "ldap/base": {
        "name": "ldap_base"
    },
    "ox/context/id": {
        "name": "ox_default_context"
    }
}

for ucr_key, config in ucr_mappings.items():
    try:
        if "transform_cb" in config:
            configs[config["name"]] = config["transform_cb"](ucr.get(ucr_key, None))
        else:
            configs[config["name"]] = ucr.get(ucr_key, None)
    except:
        configs[config["name"]] = None

configs["provisioning_admin_user"] = "admin"
with open("/etc/provisioning-secrets.json", "r") as file:
    configs["provisioning_admin_password"] = json.load(file)["PROVISIONING_API_ADMIN_PASSWORD"]

configs["ldap_admin_user"] = "cn=admin"
configs["ldap_admin_password"] = Path("/etc/ldap.secret").read_text().strip()

ox_connector_env = dotenv_values("/var/lib/univention-appcenter/apps/ox-connector/ox-connector.env")

configs["ox_master_admin"] = ox_connector_env["OX_MASTER_ADMIN"]
configs["ox_master_password"] = ox_connector_env["OX_MASTER_PASSWORD"]
configs["ox_deputy_permissions"] = ox_connector_env["OX_ENABLE_DEPUTY_PERMISSIONS"]
configs["ox_shared_accounts"] = ox_connector_env["OX_ENABLE_SHARED_ACCOUNT"]
configs["ox_soap_server"] = ox_connector_env["OX_SOAP_SERVER"]
configs["ox_imap_server"] = ox_connector_env["OX_IMAP_SERVER"]
configs["ox_smtp_server"] = ox_connector_env["OX_SMTP_SERVER"]
configs["ox_db_connection_string"] = ox_connector_env["OX_CONNECTOR_DB"]

parsed_url = urlparse(configs["ox_soap_server"])
host_ip = to_ip(parsed_url.hostname)

configs["hosts"] = [{
    "ip": host_ip,
    "hosts": [
        parsed_url.hostname,
    ]
  }
]

print(json.dumps(configs))
"""
        with self._connect() as ssh_client:
            result = self._run(ssh_client, f"python3 -c '{python_code}'")

        remote_config = json.loads(result.strip())

        remote_config["provisioning_api_base_url"] = (
            f"http://{remote_config['provisioning_api_host']}:{remote_config['provisioning_api_port']}"
        )

        remote_config["ox_secret_file"] = "/tmp/contexts.json"
        remote_config["create_own_subscription"] = True

        return remote_config

    def patch_aiohttp_session(self, session):
        pass

    def patch_sqlalchemy_engine(self, engine):
        pass
