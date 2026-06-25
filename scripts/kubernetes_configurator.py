#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import logging

from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.resolver import DefaultResolver
from configurator import RemoteConfigurator
from kubernetes import client, config
from kubernetes.stream import stream, portforward
from pathlib import Path
from sqlalchemy import event
from psycopg2 import extensions as ext
from portforward import PortForwarder
import threading
import base64
import yaml
import time
import socket
import tarfile
import io
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class KubernetesConfigurator(RemoteConfigurator):
    def __init__(self, namespace, sync_files):
        self.namespace = namespace
        self.ox_connector_selector = "app.kubernetes.io/name=ox-connector"
        self.ox_connector_pod_name = None
        self.sync_files = sync_files
        self.files = {}
        self.db_port_forward = None

    def _get_files(self) -> dict[str, str]:
        return {"/etc/ox-secrets/ox-contexts.json": "/tmp/contexts.json"}

    def _read_file(self, pod_name, remote_path):
        remote_path = Path(remote_path)
        remote_dir = remote_path.parent
        if not remote_dir:
            remote_dir = '.'
        remote_base = remote_path.name

        try:
            # Using tar to stream the file content
            command = [
                'tar',
                'cf',
                '-',
                '-C',
                str(remote_dir),
                str(remote_base),
            ]
            logger.info(
                f"Read '{remote_dir}/{remote_base}' from pod '{pod_name}'.",
            )
            resp = stream(
                self.client_v1.connect_get_namespaced_pod_exec,
                pod_name,
                self.namespace,
                command=command,
                stderr=False,
                stdin=False,
                stdout=True,
                tty=False,
                binary=True,
                _preload_content=False,
            )

            output_buffer = io.BytesIO()
            while resp.returncode is None and resp.is_open():
                resp.update()
                if resp.peek_stdout():
                    output_buffer.write(resp.read_stdout(1024))
                if resp.peek_stderr():
                    logger.error(f"STDERR: {resp.read_stderr()}")

            if resp.returncode != 0:
                logger.error("Failed to read file.")
                return None
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise e
        finally:
            resp.close()

        logger.info("Read file successful.")
        try:
            output_buffer.seek(0)
            with tarfile.open(fileobj=output_buffer, mode='r:*') as tar:
                reader = tar.extractfile(remote_base)
                return reader.read()
        except Exception as e:
            logger.error(f"Error extracting received tar: {e}")
            raise e

    def _download_file(self, pod_name, remote_path, local_path):
        local_path = Path(local_path)

        data = self._read_file(pod_name, remote_path)
        if data is None:
            return False

        target_dir = local_path.parent
        if not target_dir.exists():
            target_dir.mkdir()

        with open(local_path, "wb") as outfile:
            outfile.write(data)

        logger.info(f"Saved local file: {local_path}")
        return True

    def _upload_file(self, pod_name, local_path, remote_path):
        local_path = Path(local_path)
        if not local_path.exists():
            return

        remote_path = Path(remote_path)
        remote_dir = remote_path.parent
        if not remote_dir:
            remote_dir = '.'
        remote_base = remote_path.name

        tar_buffer = io.BytesIO()
        try:
            with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
                tar.add(local_path, arcname=remote_base)
            tar_buffer.seek(0)
        except Exception as e:
            logger.error(f"Error creating local tarball: {e}")
            raise e

        command = f"mkdir -p {remote_dir} && tar -xf - -C {remote_dir}"

        try:
            logger.info(
                f"Uploading '{local_path}' to '{pod_name}:{remote_path}'",
            )
            resp = stream(
                self.client_v1.connect_get_namespaced_pod_exec,
                pod_name,
                self.namespace,
                command=["/bin/sh", "-c", command],
                stdin=True,
                stderr=True,
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            while resp.returncode is None and resp.is_open():
                resp.update()
                if resp.peek_stdout():
                    logger.info(f"STDOUT: {resp.read_stdout()}")
                if resp.peek_stderr():
                    logger.error(f"STDERR: {resp.read_stderr()}")

                data = tar_buffer.read(1024)
                if len(data) > 0:
                    resp.write_stdin(data)

            if resp.returncode == 0:
                logger.info("Upload successful.")
            else:
                logger.error("Failed to upload file.")
                raise Exception("Error uploading file")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise e
        finally:
            resp.close()

    def _get_pod_name_by_label(self, label_selector):
        pods = self.client_v1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_selector,
        )
        if not pods.items:
            raise ValueError(
                f"Failed to find pod with label {label_selector} in {self.namespace}",
            )

        for pod in pods.items:
            is_job = False
            for owner_reference in pod.metadata.owner_references:
                if owner_reference.kind == "Job":
                    is_job = True
                    break

            if is_job:
                continue

            return pod.metadata.name

        raise ValueError(
            f"Failed to get pod: label_selector={label_selector}, namespace={self.namespace}",
        )

    def _get_api(self):
        config.load_kube_config()
        self.client_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()

        assert (
            self.client_v1 is not None and self.apps_v1 is not None
        ), f"Failed to create kubernetes client from config {os.environ['KUBE_CONFIG']}"

    def _get_ready_replicas(self, resources):
        ready_replicas = 0
        for res in resources:
            if res['type'] == 'deployment':
                dep = self.apps_v1.read_namespaced_deployment(
                    name=res['name'],
                    namespace=self.namespace,
                )
                ready_replicas += dep.status.ready_replicas or 0
            elif res['type'] == 'statefulset':
                stateful_set = self.apps_v1.read_namespaced_stateful_set(
                    name=res['name'],
                    namespace=self.namespace,
                )
                ready_replicas += stateful_set.status.ready_replicas or 0

        return ready_replicas

    def _wait_for_resources(self, resources, desired_replicas, timeout):
        logger.info(
            f"Waiting for resources to reach {desired_replicas} replicas (timeout: {timeout}s)...",
        )
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_ready = self._get_ready_replicas(resources)
            if current_ready == desired_replicas:
                logger.info("All resources are ready.")
                return

            logger.info(
                f"[WAITING] {current_ready}/{desired_replicas} ready",
            )
            time.sleep(5)

        raise Exception("Timeout reached! Some resources are not be ready.")

    def _get_resources(self, label_selector):
        resources = []
        deployments = self.apps_v1.list_namespaced_deployment(
            namespace=self.namespace,
            label_selector=label_selector,
        )
        for dep in deployments.items:
            resources.append(
                {'type': 'deployment', 'name': dep.metadata.name},
            )

        stateful_sets = self.apps_v1.list_namespaced_stateful_set(
            namespace=self.namespace,
            label_selector=label_selector,
        )
        for stateful_set in stateful_sets.items:
            resources.append(
                {
                    'type': 'statefulset',
                    'name': stateful_set.metadata.name,
                },
            )

        if not deployments.items and not stateful_sets.items:
            logger.error(
                f"No Deployments or StatefulSets found matching label '{label_selector}' in namespace '{self.namespace}'.",
            )

        return resources

    def _scale_resources(self, label_selector, replicas, wait):
        body = {"spec": {"replicas": replicas}}
        scaled_resources = self._get_resources(label_selector)

        try:
            for res in scaled_resources:
                if res['type'] == 'deployment':
                    self.apps_v1.patch_namespaced_deployment_scale(
                        name=res['name'],
                        namespace=self.namespace,
                        body=body,
                    )
                    logger.info(
                        f"Deployment '{res['name']}' matched label '{label_selector}' and was scaled to {replicas} replicas.",
                    )
                elif res['type'] == 'statefulset':
                    self.apps_v1.patch_namespaced_stateful_set_scale(
                        name=res['name'],
                        namespace=self.namespace,
                        body=body,
                    )
                    logger.info(
                        f"StatefulSet '{res['name']}' matched label '{label_selector}' and was scaled to {replicas} replicas.",
                    )
        except Exception as e:
            logger.error(f"Error scaling by label '{label_selector}': {e}")

        if scaled_resources:
            self._wait_for_resources(scaled_resources, replicas, 300)

    def __enter__(self):
        self._get_api()
        if not self.sync_files:
            return self

        ox_connector_resources = self._get_resources(
            self.ox_connector_selector,
        )
        if self._get_ready_replicas(ox_connector_resources) > 0:
            self.ox_connector_pod_name = self._get_pod_name_by_label(
                self.ox_connector_selector,
            )

            for remote, local in self._get_files().items():
                if self._download_file(
                    self.ox_connector_pod_name,
                    remote,
                    local,
                ):
                    self.files[remote] = local

        self._scale_resources(self.ox_connector_selector, 0, True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db_port_forward:
            self.db_port_forward.stop()

        if not self.sync_files:
            return

        self._scale_resources(self.ox_connector_selector, 1, False)

        if self.ox_connector_pod_name is not None:
            for remote, local in self.files.items():
                self._upload_file(self.ox_connector_pod_name, local, remote)

    def _get_configuration(self, label_selector):
        specs = []
        deployment_sets = self.apps_v1.list_namespaced_deployment(
            namespace=self.namespace,
            label_selector=label_selector,
        )
        stateful_sets = self.apps_v1.list_namespaced_stateful_set(
            namespace=self.namespace,
            label_selector=label_selector,
        )
        jobs = self.batch_v1.list_namespaced_job(
            namespace=self.namespace,
            label_selector=label_selector,
        )
        for resource in deployment_sets.items:
            specs.append(resource.spec.template.spec)
        for resource in stateful_sets.items:
            specs.append(resource.spec.template.spec)
        for resource in jobs.items:
            specs.append(resource.spec.template.spec)

        spec_env = {}
        config_maps = set()
        secret_envs = {}
        secret_env_from = set()

        for spec in specs:
            # Check containers for env and env_from
            for container in spec.containers:
                # Check env
                if container.env:
                    for env in container.env:
                        if env.value_from:
                            if env.value_from.config_map_key_ref:
                                config_maps.add(
                                    env.value_from.config_map_key_ref.name,
                                )
                            elif env.value_from.secret_key_ref:
                                secret_envs[env.name] = {
                                    "key": env.value_from.secret_key_ref.key,
                                    "name": env.value_from.secret_key_ref.name,
                                }
                        elif env.value:
                            spec_env[env.name] = env.value

                # Check env_from
                if container.env_from:
                    for ef in container.env_from:
                        if ef.config_map_ref:
                            config_maps.add(ef.config_map_ref.name)
                        elif ef.secret_ref:
                            secret_env_from.add(ef.secret_ref.name)

            # Check volumes
            if spec.volumes:
                for vol in spec.volumes:
                    if vol.config_map:
                        config_maps.add(vol.config_map.name)
                    if vol.projected:
                        for source in vol.projected.sources:
                            if source.config_map:
                                config_maps.add(source.config_map.name)

            if config_maps:
                for cm_name in config_maps:
                    try:
                        cm = self.client_v1.read_namespaced_config_map(
                            name=cm_name,
                            namespace=self.namespace,
                        )
                        if cm.data:
                            for k, v in cm.data.items():
                                spec_env[k] = v
                    except Exception as e:
                        logging.error(
                            f"  Error reading ConfigMap {cm_name}: {e}",
                        )

            if secret_envs:
                for env_name, secret in secret_envs.items():
                    try:
                        sec = self.client_v1.read_namespaced_secret(
                            name=secret["name"],
                            namespace=self.namespace,
                        )
                        if sec.data and secret["key"] in sec.data:
                            v = sec.data[secret["key"]]
                            decoded_v = base64.b64decode(v).decode('utf-8')
                            spec_env[env_name] = decoded_v
                    except Exception as e:
                        logging.error(
                            f"  Error reading Secret {secret['name']}: {e}",
                        )

            if secret_env_from:
                for secret in secret_env_from:
                    try:
                        sec = self.client_v1.read_namespaced_secret(
                            name=secret,
                            namespace=self.namespace,
                        )
                        for k, v in sec.data.items():
                            decoded_v = base64.b64decode(v).decode('utf-8')
                            spec_env[k] = decoded_v
                    except Exception as e:
                        logging.error(f"  Error reading Secret {secret}: {e}")

        return spec_env

    def get_configurations(self) -> dict:
        ox_connector_config = self._get_configuration(
            self.ox_connector_selector,
        )
        ox_core_mw_config = self._get_configuration(
            "app.kubernetes.io/name=core-mw",
        )
        udm_rest_api_config = self._get_configuration(
            "app.kubernetes.io/name=udm-rest-api",
        )
        ldap_server_config = self._get_configuration(
            "app.kubernetes.io/name=ldap-server",
        )
        umc_gateway = self._get_configuration(
            "app.kubernetes.io/name=umc-gateway",
        )

        ucr_base_config = {}
        for line in umc_gateway['base.conf'].splitlines():
            if len(line) == 0 or line.startswith("#"):
                continue

            key, value = line.strip().split(':', 1)
            ucr_base_config[key.strip()] = value.strip()

        ox_core_mw_properties = yaml.safe_load(
            ox_core_mw_config['996_properties.yaml'],
        )

        remote_config = {}
        remote_config["provisioning_api_base_url"] = ox_connector_config[
            "PROVISIONING_API_BASE_URL"
        ]
        remote_config["ox_master_admin"] = ox_connector_config[
            "OX_MASTER_ADMIN"
        ]
        remote_config["ox_master_password"] = ox_connector_config[
            "OX_MASTER_PASSWORD"
        ]
        remote_config["ldap_server"] = (
            f"{ucr_base_config['hostname']}.{ucr_base_config['domainname']}"
        )
        remote_config["ldap_base"] = ldap_server_config["LDAP_BASEDN"]
        remote_config["ldap_admin_user"] = udm_rest_api_config["UDM_API_USER"]
        remote_config["ldap_admin_password"] = self._read_file(
            self._get_pod_name_by_label("app.kubernetes.io/name=udm-rest-api"),
            udm_rest_api_config["UDM_API_PASSWORD_FILE"],
        ).decode("utf-8")

        remote_config["domain_name"] = ucr_base_config['domainname']
        remote_config["ox_default_context"] = ox_connector_config[
            "DEFAULT_CONTEXT"
        ]
        remote_config["ox_deputy_permissions"] = ox_connector_config[
            "OX_ENABLE_DEPUTY_PERMISSIONS"
        ]
        remote_config["ox_shared_accounts"] = ox_connector_config[
            "OX_ENABLE_SHARED_ACCOUNT"
        ]
        remote_config["ox_soap_server"] = (
            f"https://{ox_core_mw_properties['anywhere']['com.openexchange.hostname']}"
        )

        if (
            'com.openexchange.client.onboarding.mail.imap.host'
            in ox_core_mw_properties['anywhere']
            and 'com.openexchange.client.onboarding.mail.imap.port'
            in ox_core_mw_properties['anywhere']
        ):
            imap_server = f"imaps://{ox_core_mw_properties['anywhere']['com.openexchange.client.onboarding.mail.imap.host']}:{ox_core_mw_properties['anywhere']['com.openexchange.client.onboarding.mail.imap.port']}"
        else:
            imap_server = "imap://dovecot-ce:143"

        if (
            'com.openexchange.client.onboarding.mail.smtp.host'
            in ox_core_mw_properties['anywhere']
            and 'com.openexchange.client.onboarding.mail.smtp.port'
            in ox_core_mw_properties['anywhere']
        ):
            smtp_server = f"smtp://{ox_core_mw_properties['anywhere']['com.openexchange.client.onboarding.mail.smtp.host']}:{ox_core_mw_properties['anywhere']['com.openexchange.client.onboarding.mail.smtp.port']}"
        else:
            smtp_server = "stub-value"

        remote_config["ox_imap_server"] = imap_server
        remote_config["ox_smtp_server"] = smtp_server
        remote_config["ox_secret_file"] = "/tmp/contexts.json"

        remote_config["udm_user"] = udm_rest_api_config["UDM_API_USER"]
        remote_config["udm_password"] = remote_config["ldap_admin_password"]

        remote_config["create_own_subscription"] = False
        remote_config["provisioning_api_username"] = ox_connector_config[
            "PROVISIONING_API_USERNAME"
        ]
        remote_config["provisioning_api_password"] = ox_connector_config[
            "PROVISIONING_API_PASSWORD"
        ]
        remote_config["ox_db_connection_string"] = ox_connector_config[
            "OX_CONNECTOR_DB"
        ]

        return remote_config

    def _is_kubernetes_service(self, dns_name):
        if (
            len(dns_name) >= 3
            and dns_name[1] == self.namespace
            and dns_name[2] in ("svc", "service")
        ):
            return True

        if len(dns_name) == 1:
            service = self.client_v1.read_namespaced_service(
                dns_name[0],
                self.namespace,
            )
            return service is not None

        return False

    def _get_pod_name_and_port_from_service(self, service_name, service_port):
        service = self.client_v1.read_namespaced_service(
            service_name,
            self.namespace,
        )
        for service_ports in service.spec.ports:
            if service_ports.port == int(service_port):
                port = service_ports.target_port
                break
        else:
            raise RuntimeError(f"Unable to find service port: {service_port}")

        label_selector = []
        for key, value in service.spec.selector.items():
            label_selector.append(f"{key}={value}")
        pods = self.client_v1.list_namespaced_pod(
            self.namespace,
            label_selector=",".join(label_selector),
        )
        if not pods.items:
            raise RuntimeError("Unable to find service pods.")

        name = pods.items[0].metadata.name
        if isinstance(port, str):
            for container in pods.items[0].spec.containers:
                for container_port in container.ports:
                    if container_port.name == port:
                        port = container_port.container_port
                        break
                else:
                    continue
                break
            else:
                raise RuntimeError(
                    f"Unable to find service port name: {port}",
                )

        return name, port

    def patch_aiohttp_session(self, session):
        resolver = DefaultResolver()
        resolve_orig = resolver.resolve

        async def patched_resolve(
            host: str,
            port: int = 0,
            family: socket.AddressFamily = socket.AF_INET,
        ):
            dns_name = host.split(".")
            if not self._is_kubernetes_service(dns_name):
                return await resolve_orig(host, port, family)

            logger.info(f"Intercept DNS for port forward: {dns_name}")
            return [
                {
                    "hostname": host,
                    "host": host,
                    "port": port,
                    "family": family,
                    "proto": 0,
                    "flags": 0,
                },
            ]

        resolver.resolve = patched_resolve
        session._connector._resolver = resolver

        wrap_create_connection_orig = (
            session._connector._wrap_create_connection
        )

        async def patched_wrap_create_connection(
            *args,
            addr_infos,
            req,
            timeout,
            client_error=ClientConnectorError,
            **kwargs,
        ):
            for addr_info in addr_infos:
                family, type_, proto, _, ip_port = addr_info
                ip, port = ip_port

                dns_name = ip.split(".")
                if not self._is_kubernetes_service(dns_name):
                    return wrap_create_connection_orig(
                        *args,
                        addr_infos=addr_infos,
                        req=req,
                        timeout=timeout,
                        client_error=client_error,
                        **kwargs,
                    )

                service = dns_name[0]
                name, port = self._get_pod_name_and_port_from_service(
                    service,
                    port,
                )

                logger.info(f"Using kubernetes port forward: {name}:{port}")
                pf = portforward(
                    self.client_v1.connect_get_namespaced_pod_portforward,
                    name,
                    self.namespace,
                    ports=str(port),
                )
                return await session._connector._loop.create_connection(
                    *args,
                    **kwargs,
                    sock=pf.socket(port),
                )

        session._connector._wrap_create_connection = (
            patched_wrap_create_connection
        )

    def patch_sqlalchemy_engine(self, engine):
        configurator = self

        class KubernetesPortForwaringFactory(ext.connection):
            def __init__(self, dsn, async_=0):
                parsed_dsn = ext.parse_dsn(dsn)
                dns_name = parsed_dsn["host"].split(".")
                if configurator._is_kubernetes_service(dns_name):
                    logger.info(parsed_dsn)
                    service = dns_name[0]
                    name, port = (
                        configurator._get_pod_name_and_port_from_service(
                            service,
                            parsed_dsn["port"],
                        )
                    )

                    local_port = 0
                    with socket.socket(
                        socket.AF_INET,
                        socket.SOCK_STREAM,
                    ) as s:
                        s.bind(('', local_port))
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        local_port = s.getsockname()[1]

                    parsed_dsn["host"] = "localhost"
                    parsed_dsn["port"] = local_port
                    dsn = ext.make_dsn(**parsed_dsn)

                    port_forward_finished = threading.Condition()

                    def port_forward_func():
                        logger.info(
                            f"Using portforwarding: {name}:{port} -> localhost:{local_port}",
                        )
                        configurator.db_port_forward = PortForwarder(
                            configurator.namespace,
                            name,
                            local_port,
                            port,
                        )
                        configurator.db_port_forward.forward()
                        logger.info("Port forwarding setup finished")
                        with port_forward_finished:
                            port_forward_finished.notify()

                    t = threading.Thread(target=port_forward_func)
                    t.start()
                    with port_forward_finished:
                        port_forward_finished.wait()

                ext.connection.__init__(self, dsn, async_=async_)

        @event.listens_for(engine, "do_connect")
        def receive_do_connect(dialect, conn_rec, cargs, cparams):
            logger.info(
                f"Intercept do_connect to use kubernes port forwarding connection factory: {conn_rec}",
            )
            cparams["connection_factory"] = KubernetesPortForwaringFactory
