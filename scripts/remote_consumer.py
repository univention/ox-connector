# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
Standalone Consumer Remote Control.

Runs consumer locally using configurations fetched from remote hosts.
"""

import asyncio
import argparse
import contextlib
import sys
import os
import json
import traceback

import logging
from typing import Optional
from pathlib import Path
from univention.provisioning.consumer.api import (
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
)
from univention.provisioning.models.subscription import RealmTopic
from subprocess import Popen

from .configurator import RemoteConfigurator
from .ssh_configurator import SSHConfigurator
from .kubernetes_configurator import KubernetesConfigurator

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ProvisioningSubsription:
    def __init__(
        self,
        configurator,
        base_api_url: str,
        admin_user: str,
        admin_password: str,
        subscriber_name: str,
        subscriber_password: str,
        realms_topics: list[RealmTopic],
    ):
        client_settings = ProvisioningConsumerClientSettings(
            provisioning_api_base_url=base_api_url,
            provisioning_api_username=admin_user,
            provisioning_api_password=admin_password,
            log_level="DEBUG",
        )

        self.client = ProvisioningConsumerClient(client_settings)
        configurator.patch_aiohttp_session(self.client.session)

        self.subscriber_name = subscriber_name
        self.subscriber_password = subscriber_password
        self.realms_topics = realms_topics

    async def __aenter__(self):
        await self.client.create_subscription(
            name=self.subscriber_name,
            password=self.subscriber_password,
            realms_topics=self.realms_topics,
            request_prefill=False,
        )

        return self

    async def __aexit__(self, *args):
        await self.client.cancel_subscription(self.subscriber_name)
        await self.client.close()


class RemoteConsumer:
    """Manage remote ox-connector deployments via configurable backend."""

    def __init__(self, configurator: RemoteConfigurator, timeout: int = 300):
        """Initialize with configurable backend.

        Args:
            configurator: Remote configurator
            timeout: Command timeout in seconds
        """
        self.configurator = configurator
        self.timeout = timeout

    def get_configurations(self) -> dict:
        """Fetch and return configurations from remote host."""
        try:
            return self.configurator.get_configurations()
        except Exception as e:
            logger.error(f"Failed to fetch configurations: {e}")
            return {}

    async def run_consumer(self, restart: bool) -> bool:
        """
        Fetch configurations and run consumer locally.

        Args:
            debug: Run with python debugger

        Returns:
            True if consumer ran successfully
        """
        configs = self.get_configurations()

        if not configs:
            logger.warning("No configurations available")
            return -1

        if configs['create_own_subscription']:
            subscriber_name = "ox-connector-dev"
            subscriber_password = "ox-connector-dev"

            cm = ProvisioningSubsription(
                self.configurator,
                configs["provisioning_api_base_url"],
                configs["provisioning_admin_user"],
                configs["provisioning_admin_password"],
                subscriber_name,
                subscriber_password,
                [
                    RealmTopic(realm="udm", topic="users/user"),
                    RealmTopic(realm="udm", topic="groups/group"),
                    RealmTopic(realm="udm", topic="oxmail/oxcontext"),
                    RealmTopic(realm="udm", topic="oxmail/accessprofile"),
                    RealmTopic(realm="udm", topic="oxresources/oxresources"),
                    RealmTopic(realm="udm", topic="oxmail/functional_account"),
                    RealmTopic(realm="udm", topic="oxmail/shared_account"),
                    RealmTopic(
                        realm="udm",
                        topic="oxmail/shared_account_permission",
                    ),
                ],
            )
        else:
            subscriber_name = configs["provisioning_api_username"]
            subscriber_password = configs["provisioning_api_password"]

            cm = contextlib.nullcontext()

        async with cm:
            # Set environment variables from fetched configurations
            os.environ["LOG_LEVEL"] = "DEBUG"
            os.environ["PROVISIONING_API_BASE_URL"] = configs[
                "provisioning_api_base_url"
            ]
            os.environ["PROVISIONING_API_USERNAME"] = subscriber_name
            os.environ["PROVISIONING_API_PASSWORD"] = subscriber_password
            os.environ["MAX_ACKNOWLEDGEMENT_RETRIES"] = "3"

            os.environ["DOMAINNAME"] = configs["domain_name"]
            os.environ["OX_MASTER_ADMIN"] = configs["ox_master_admin"]
            os.environ["OX_MASTER_PASSWORD"] = configs["ox_master_password"]
            os.environ["OX_SMTP_SERVER"] = configs["ox_smtp_server"]
            os.environ["OX_IMAP_SERVER"] = configs["ox_imap_server"]
            os.environ["OX_SOAP_SERVER"] = configs["ox_soap_server"]
            os.environ["DEFAULT_CONTEXT"] = configs["ox_default_context"]
            os.environ["OX_CREDENTIALS_FILE"] = configs["ox_secret_file"]
            os.environ["OX_ENABLE_DEPUTY_PERMISSIONS"] = configs[
                "ox_deputy_permissions"
            ]
            os.environ["OX_ENABLE_SHARED_ACCOUNT"] = configs[
                "ox_shared_accounts"
            ]
            os.environ["OX_CONNECTOR_DB"] = configs["ox_db_connection_string"]
            os.environ["OX_USER_IDENTIFIER"] = configs["user_identifier"]
            os.environ["OX_GROUP_IDENTIFIER"] = configs["group_identifier"]
            os.environ["OX_SHARED_ACCOUNT_IDENTIFIER"] = configs[
                "shared_account_identifier"
            ]

            if "hosts" in configs:
                with open("/etc/hosts", 'a') as file:
                    for host in configs["hosts"]:
                        file.write(f"{host['ip']} {' '.join(host['hosts'])}\n")

            # dir is hardcoded in consumer.py
            Path(
                "/var/lib/univention-appcenter/apps/ox-connector/data/",
            ).mkdir(exist_ok=True, parents=True)
            # start with a clean test.log
            Path("/tmp/test.log").unlink(missing_ok=True)

            logger.info(f"Applied configurations: {configs}")

            sys.path.insert(0, "/")

            from univention.ox.provisioning.db import engine

            self.configurator.patch_sqlalchemy_engine(engine)

            from consumer import _run_consumer_with_guard

            def create_provisioning_client():
                provisioning_consumer = ProvisioningConsumerClient()
                self.configurator.patch_aiohttp_session(
                    provisioning_consumer.session,
                )

                return provisioning_consumer

            restarts_done = 0
            while True:
                try:
                    sys.argv = [sys.argv[0]]
                    await _run_consumer_with_guard(create_provisioning_client)
                except asyncio.exceptions.CancelledError:
                    logger.info("Mainloop cancelled -> shutting down")
                    break
                except Exception as e:
                    if restart:
                        restarts_done += 1
                        print(traceback.format_exc())
                    else:
                        raise e

            if restart:
                logger.info(
                    f"Consumer was restarted {restarts_done} times",
                )

            return 0

    def run_tests(
        self,
        udm_username: str | None,
        udm_password: str | None,
        command: Optional[list[str]] = None,
    ) -> bool:
        configs = self.get_configurations()

        if not configs:
            logger.warning("No configurations available")
            return False

        # Set environment variables from fetched configurations
        test_env = os.environ.copy()
        test_env["LOG_LEVEL"] = "DEBUG"
        test_env["DOMAINNAME"] = configs["domain_name"]
        if udm_username is not None:
            test_env["TESTS_UDM_ADMIN_USERNAME"] = udm_username
        else:
            test_env["TESTS_UDM_ADMIN_USERNAME"] = configs["udm_user"]

        if udm_password is not None:
            test_env["TESTS_UDM_ADMIN_PASSWORD"] = udm_password
        else:
            test_env["TESTS_UDM_ADMIN_PASSWORD"] = configs["udm_password"]

        test_env["LDAP_BASE"] = configs["ldap_base"]
        test_env["DEFAULT_CONTEXT"] = configs["ox_default_context"]
        test_env["LDAP_MASTER"] = configs["ldap_server"]
        test_env["OX_CREDENTIALS_FILE"] = configs["ox_secret_file"]
        test_env["OX_SMTP_SERVER"] = configs["ox_smtp_server"]
        test_env["OX_IMAP_SERVER"] = configs["ox_imap_server"]
        test_env["OX_SOAP_SERVER"] = configs["ox_soap_server"]
        test_env["OX_ENABLE_DEPUTY_PERMISSIONS"] = configs[
            "ox_deputy_permissions"
        ]
        test_env["OX_ENABLE_SHARED_ACCOUNT"] = configs["ox_shared_accounts"]
        test_env["OX_USER_IDENTIFIER"] = configs["user_identifier"]
        test_env["OX_GROUP_IDENTIFIER"] = configs["group_identifier"]
        test_env["OX_SHARED_ACCOUNT_IDENTIFIER"] = configs[
            "shared_account_identifier"
        ]

        if "hosts" in configs:
            with open("/etc/hosts", 'a') as file:
                for host in configs["hosts"]:
                    file.write(f"{host['ip']} {' '.join(host['hosts'])}\n")

        logger.info(f"Applied configurations: {configs}")

        # Run consumer locally using subprocess with environment
        cmd = ["python3", "-m", "pytest", "tests"]
        if command:
            cmd.extend(command)

        logger.info(f"Running tests with command: {' '.join(cmd)}")
        with Popen(
            cmd,
            env=test_env,
            stdout=sys.stdout,
            stderr=sys.stderr,
        ) as proc:
            exit_code = proc.wait()
            logger.info(f"Test exit code: {exit_code}")

            return exit_code == 0

    def run_udm(self, udm_args: list[str]):
        configs = self.get_configurations()

        connection_args = [
            "--uri",
            f"https://{configs['ldap_server']}/univention/udm/",
            "--binddn",
            configs["ldap_admin_user"],
            "--bindpwd",
            configs["ldap_admin_password"],
        ]

        udm_cmd = connection_args + udm_args
        logger.info(f"Running udm with: {' '.join(udm_cmd)}")
        from univention.admin.rest.client.__main__ import (
            main as udm_client_main,
        )

        udm_client_main(arg_list=udm_cmd)

    def run_task_management(self, tm_args: list[str]):
        configs = self.get_configurations()

        os.environ["OX_CONNECTOR_DB"] = configs["ox_db_connection_string"]

        from univention.ox.provisioning.db import engine

        self.configurator.patch_sqlalchemy_engine(engine)

        tm_cmd = tm_args
        if tm_cmd and tm_cmd[0] == "resync-item":
            tm_cmd = [
                *tm_cmd,
                "--udm-uri",
                f"https://{configs['ldap_server']}/univention/udm/",
                "--udm-user",
                configs["ldap_admin_user"],
                "--udm-password",
                configs["ldap_admin_password"],
            ]
        logger.info(f"Running task-management with: {' '.join(tm_cmd)}")

        sys.path.insert(0, "share/")

        import importlib

        task_manager = importlib.import_module(
            "univention-ox-connector-task-management",
        )

        task_manager._call("show-items")


def create_configurator(args) -> RemoteConfigurator:
    if args.mode == "ssh":
        return SSHConfigurator(
            host=args.host,
            user=args.user,
            password=args.password,
            sync_files=args.command == "run",
        )
    elif args.mode == "kubernetes":
        return KubernetesConfigurator(
            namespace=args.namespace,
            sync_files=args.command == "run",
            keep_off=args.keep_off if args.command == "run" else False,
        )
    else:
        raise ValueError(f"Unknown mode: {args.mode}")


def add_command_parser(parser, parser_type):
    command_subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
    )

    # Configurations command
    command_subparsers.add_parser(
        "configurations",
        help="Fetch and print configurations from remote deployment",
    )

    # Run command
    run_parser = command_subparsers.add_parser(
        "run",
        help="Run consumer locally using fetched configurations",
    )
    run_parser.add_argument(
        "-r",
        "--restart",
        help="Restart consumer ith exit code is != 0",
        action="store_true",
    )
    run_parser.add_argument(
        "-k",
        "--keep-off",
        help="Keep the original consumer off, do not restart it",
        action="store_true",
    )

    # Test command
    test_parser = command_subparsers.add_parser(
        "test",
        help="Run tests locally using fetched configurations",
    )
    test_parser.add_argument(
        "--udm_username",
        help="Username to connect to UDM/UCM",
        default="Administrator" if parser_type == "ssh" else None,
    )
    test_parser.add_argument(
        "--udm_password",
        help="Password to connect to UDM/UCM",
        default="univention" if parser_type == "ssh" else None,
    )

    # Udm command
    command_subparsers.add_parser(
        "udm",
        help="Run udm rest client, can be used to fix/delete objects in case connector or tests crash and cleanup was not done properly",
    )

    # Task management command
    command_subparsers.add_parser(
        "task-management",
        help="Run univention-ox-connector-task-management locally using remote UDM configuration",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Remote ox-connector Consumer Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  configurations <mode> <target>          Fetch and print configurations
  run <mode> <target>                     Run consumer
  test <mode> <target> <pytest_args>      Run tests
  udm <mode> <target> <udm_args>          Run UDM command
  task-management <mode> <target> <tm_args> Run task-management command using remote configuration
  help                                    Show this help

Arguments:
  mode: ssh or kubernetes
  target: Host address (ssh) or namespace (kubernetes)

Examples:
  %(prog)s configurations ssh 192.168.1.100
  %(prog)s run ssh 192.168.1.100
  %(prog)s test ssh 192.168.1.100
""",
    )

    mode_subparsers = parser.add_subparsers(
        dest="mode",
        help="Mode: ssh or kubernetes",
    )

    ssh_parser = mode_subparsers.add_parser(
        "ssh",
        help="Run in ssh mode used for UCS deployments",
    )
    ssh_parser.add_argument("host", help="Remote host to connect to via ssh")
    ssh_parser.add_argument(
        "-u",
        "--user",
        help="Use user for ssh login",
        default="root",
    )
    ssh_parser.add_argument(
        "-p",
        "--password",
        help="use password for ssh login",
        default="univention",
    )

    kubernetes_parser = mode_subparsers.add_parser(
        "kubernetes",
        help="Run in kubernetes mode",
    )
    kubernetes_parser.add_argument(
        "namespace",
        help="Kubernetes namespace of the remote OX deployment",
    )

    add_command_parser(ssh_parser, "ssh")
    add_command_parser(kubernetes_parser, "kubernetes")

    args, rest = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    with create_configurator(args) as configurator:
        remote = RemoteConsumer(configurator)

        try:
            if args.command == "configurations":
                configs = remote.get_configurations()
                print(json.dumps(configs, indent=2))
            elif args.command == "run":
                asyncio.run(remote.run_consumer(args.restart))
            elif args.command == "test":
                remote.run_tests(args.udm_username, args.udm_password, rest)
            elif args.command == "udm":
                remote.run_udm(rest)
            elif args.command == "task-management":
                remote.run_task_management(rest)
        except KeyboardInterrupt:
            logger.info(
                "Program interrupted by user (Ctrl+C). Shutting down...",
            )


if __name__ == "__main__":
    main()
