# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Kubernetes support utilities.

This module provides support utilities and fixtures for the test suite to run
against a Kubernetes deployment of the ox connector.

There are similarities with the Kubernetes related fixtures of the e2e tests in
https://git.knut.univention.de/univention/dev/nubus-for-k8s/e2e-tests.
"""

import dbm.gnu
import io
import json
import logging
import math
import os
import shlex
import subprocess
import tarfile
import tempfile
import time
import typing
from contextlib import contextmanager, closing
from kubernetes import config, client
from kubernetes.stream import stream

import pytest
from dateutil.parser import isoparse
from urllib3.exceptions import ReadTimeoutError

from utils import BaseFileUtility, BaseLogs
from univention.ox.soap import config as ox_config

log = logging.getLogger(__name__)


class KubernetesCluster:
    """
    Fixture which represents the Kubernetes cluster.
    """

    def __init__(self, namespace: str):
        self.load_config()
        self.namespace = namespace

    def load_config(self):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

    def get_pod_name_by_label(self, label_selector: str) -> str:
        """Return the first running pod's name matching label_selector in the cluster namespace."""
        v1 = client.CoreV1Api()

        pods = v1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_selector,
            timeout_seconds=5,
        )

        for pod in pods.items:
            if pod.status.phase == "Running":
                return pod.metadata.name

        raise RuntimeError(
            f"No running pods found with selector '{label_selector}' in namespace '{self.namespace}'",
        )


class OxConnectorDeployment:
    """
    Representation of the ox connector deployment in the cluster.

    Provides small deployment-aware helpers that encapsulate pod selection and
    interaction with the Kubernetes streaming API.
    """

    pod_selector = "app.kubernetes.io/name=ox-connector"

    def __init__(self, k8s: KubernetesCluster):
        self.k8s = k8s
        self._v1 = client.CoreV1Api()

    @property
    def namespace(self) -> str:
        return self.k8s.namespace

    def get_pod_name(self) -> str:
        return self.k8s.get_pod_name_by_label(self.pod_selector)

    def exec_stream(self, command: typing.List[str]):
        pod_name = self.get_pod_name()
        response = stream(
            self._v1.connect_get_namespaced_pod_exec,
            pod_name,
            self.namespace,
            command=command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            binary=True,
            _preload_content=False,
        )
        return response

    @contextmanager
    def logs_stream(
        self,
        *,
        since_seconds: typing.Optional[int] = None,
        request_timeout: typing.Optional[int] = None,
    ):
        """
        Context manager that yields a text stream (io.TextIOBase) of pod logs.
        """
        pod = self.get_pod_name()
        raw_stream = self._v1.read_namespaced_pod_log(
            name=pod,
            namespace=self.namespace,
            since_seconds=since_seconds,
            follow=True,
            timestamps=True,
            _preload_content=False,
            _request_timeout=request_timeout,
        )
        with closing(raw_stream):
            with io.TextIOWrapper(raw_stream, encoding="utf-8") as text_stream:
                yield text_stream

    @contextmanager
    def get_file_as_tempfile(
        self,
        filepath: typing.Union[os.PathLike, str],
        mode: str = "rb",
    ):
        """
        Stream a tar archive of `filepath` from the pod, extract the member and
        write it into a new NamedTemporaryFile which is yielded positioned at 0.

        Parameters:
            filepath: absolute path inside the pod to extract
            mode: file mode for the returned tempfile; if 'b' is in mode a
                  binary tempfile is returned, otherwise a text wrapper around
                  a binary tempfile is yielded (UTF-8).

        Raises:
            FileNotFoundError: if the pod reports an error on stderr while
                               streaming the tar or the member is missing.
        """
        filepath = os.fspath(filepath)
        tar_command = ["tar", "-cf", "-", "-C", "/", filepath.lstrip("/")]
        response = self.exec_stream(tar_command)
        with closing(response), tempfile.NamedTemporaryFile() as tar_tmp:
            _drain_stream_to_file(response, tar_tmp)
            with tarfile.open(fileobj=tar_tmp, mode='r') as tar:
                extracted_fileobj = _extract_file_from_tar(tar, filepath)
                data = extracted_fileobj.read()
                with tempfile.NamedTemporaryFile(mode='w+b') as extracted_tmp:
                    extracted_tmp.write(data)
                    extracted_tmp.flush()
                    extracted_tmp.seek(0)

                    if 'b' in mode:
                        yield extracted_tmp
                    else:
                        with io.TextIOWrapper(
                            extracted_tmp,
                            encoding='utf-8',
                        ) as text_wrapper:
                            yield text_wrapper


class KubernetesFileUtility(BaseFileUtility):
    """
    Kubernetes-backed implementation that reads files from pods.
    """

    def __init__(self, deployment: OxConnectorDeployment):
        self.deployment = deployment

    @contextmanager
    def open(self, filepath: typing.Union[os.PathLike, str], mode: str = "r"):
        with self.deployment.get_file_as_tempfile(filepath, mode=mode) as tmp:
            yield tmp

    @contextmanager
    def open_dbm(
        self,
        filepath: typing.Union[os.PathLike, str],
        mode: str = "r",
    ):
        with self.deployment.get_file_as_tempfile(
            filepath,
            mode='rb',
        ) as extracted_tmp:
            with dbm.gnu.open(extracted_tmp.name, mode) as db:
                yield db


class KubernetesLogs(BaseLogs):
    """
    Kubernetes-backed implementation to monitor the logs.

    The implementation has two mechanisms to receive the logs:

    - One using the streaming API which is the preferred approach, but does
      sometimes suffer from limited fsnotify resources.

    - The second implementation uses polling and will see some log lines twice.
      This is ok for the checks, but it will lead to cluttered output if using
      flags like `--log-cli-level=info` in the testrun.
    """

    def __init__(
        self,
        deployment: OxConnectorDeployment,
        lookback_seconds: float = 5.0,
        overlap_seconds: float = 2.0,
        poll_interval: float = 0.5,
        use_polling: bool = False,
        timeout: float = 60.0,
    ):
        super().__init__(timeout)
        self.deployment = deployment
        self._overlap_seconds = overlap_seconds
        self._poll_interval = poll_interval
        self._log_position = time.time() - lookback_seconds
        self._use_polling = use_polling

    def expect_log(
        self,
        text: str,
        *,
        timeout: typing.Optional[float] = None,
    ) -> None:
        if timeout is None:
            timeout = self.timeout
        log.info("Expecting log output: %s", text)
        start_time = time.time()
        since_time = self._log_position

        if not self._use_polling:
            try:
                matched = self._expect_log_streaming(
                    text,
                    start_time,
                    since_time,
                    timeout,
                )
                if matched:
                    return
            except ReadTimeoutError:
                # NOTE: Allows to fall back into polling in case the stream call failed.
                # The polling implementation will also check the "timeout" parameter.
                log.warning(
                    "Streaming call faild with a ReadTimeoutError",
                    exc_info=True,
                )

        self._expect_log_polling(text, start_time, since_time, timeout)

    def _expect_log_streaming(
        self,
        text: str,
        start_time: float,
        since_time: float,
        timeout: float,
    ) -> bool:
        try:
            with self.deployment.logs_stream(
                since_seconds=math.ceil(time.time() - since_time),
                request_timeout=math.ceil(timeout),
            ) as text_stream:
                for line in text_stream:
                    if self._process_log_line(line, start_time, text):
                        elapsed = time.time() - start_time
                        log.info(
                            "Listener_trigger finished handling %s after %.1f seconds.",
                            text,
                            elapsed,
                        )
                        return True

                    self._fail_on_timeout(start_time, timeout, text)
        except (ValueError, OSError, io.UnsupportedOperation) as exc:
            log.warning(
                "Log stream ended unexpectedly (%s).",
                exc,
                exc_info=True,
            )

        return False

    def _expect_log_polling(
        self,
        text: str,
        start_time: float,
        since_time: float,
        timeout: float,
    ) -> None:
        if not self._use_polling:
            log.warning(
                "Kubernetes log streaming ended without matching '%s'; falling back to polling. "
                "Consider using --k8s-logs-poll to enable polling explicitly.",
                text,
            )
        while True:
            self._fail_on_timeout(start_time, timeout, text)
            since_seconds = max(
                0,
                math.ceil(time.time() - (since_time - self._overlap_seconds)),
            )
            logs = self._fetch_logs(since_seconds)
            if logs and self._process_logs(logs, start_time, text):
                elapsed = time.time() - start_time
                log.info(
                    "Listener_trigger finished handling %s after %.1f seconds.",
                    text,
                    elapsed,
                )
                return
            since_time = self._advance_since_time(since_time)
            time.sleep(self._poll_interval)

    def reset(self) -> None:
        self._log_position = time.time()
        log.debug("Reset log position")

    def _fetch_logs(self, since_seconds: int) -> typing.Optional[str]:
        try:
            logs = self.deployment._v1.read_namespaced_pod_log(
                name=self.deployment.get_pod_name(),
                namespace=self.deployment.namespace,
                since_seconds=since_seconds,
                timestamps=True,
                follow=False,
            )
            return logs
        except Exception:
            log.exception("Failed to fetch pod logs, will retry")
            return None

    def _process_logs(self, logs: str, start_time: float, text: str) -> bool:
        for line in logs.splitlines():
            if not line:
                continue
            if self._process_log_line(line, start_time, text):
                return True
        return False

    def _advance_since_time(self, since_time: float) -> float:
        return self._log_position or since_time

    def _fail_on_timeout(
        self,
        start_time: float,
        timeout: float,
        text: str,
    ) -> None:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            pytest.fail(
                f"Listener_trigger did NOT handle {text} for {elapsed:.1f} seconds.",
            )

    def _process_log_line(
        self,
        line: str,
        start_time: float,
        text: str,
    ) -> bool:
        log.info("Processing log line: %s", line)
        parsed_time = self._parse_log_timestamp(line)
        self._log_position = parsed_time or time.time()
        return text in line and "Processed: " in line

    def _parse_log_timestamp(self, line_str):
        """
        Parse the timestamp prefix out of the log line.

        The log lines are prefixed by Kubernetes with a timestamp in ISO
        format. `python-dateutil` is used to have a more robust parsing than
        the `datetime` package provides.
        """
        try:
            timestamp_str = line_str.split(' ', 1)[0]
            dt = isoparse(timestamp_str)
            return dt.timestamp()
        except ValueError:
            # NOTE: Sometimes log lines don't have a timestamp prefix, e.g. if
            # the server is running out of watchers for fsnotify.
            log.warning(
                "Cannot parse timestamp from log line: %s",
                line_str,
                exc_info=True,
            )
            return None


class K8sOXCredentialsReader:
    """
    Callable object that reads OX credentials from the running Kubernetes pod.
    """

    def __init__(self, deployment: OxConnectorDeployment):
        self.deployment = deployment

    def __call__(self):
        pod_name = self.deployment.get_pod_name()
        credentials_file_path = ox_config.CREDENTIALS_FILE
        log.info(
            "Reading ox credentials via Kubernetes API: pod_name=%s, credentials_file=%s",
            pod_name,
            credentials_file_path,
        )
        with self.deployment.get_file_as_tempfile(
            credentials_file_path,
            mode="r",
        ) as fp:
            credentials = json.load(fp)
        log.info(
            "Successfully read credentials from pod %s (file=%s)",
            pod_name,
            credentials_file_path,
        )
        return credentials


def discover_namespace() -> str:
    _, active_context = config.list_kube_config_contexts()
    if "K8S_NAMESPACE" in os.environ:
        return os.environ["K8S_NAMESPACE"]

    namespace = active_context["context"].get("namespace", "default")
    log.info("Discovered target namespace: %s", namespace)
    return namespace


def _extract_file_from_tar(tar_file, filepath: str):
    member_name = filepath.lstrip("/")
    try:
        member = tar_file.getmember(member_name)
        extracted_file = tar_file.extractfile(member)
        if extracted_file is None:
            raise FileNotFoundError(f"Could not extract {filepath} from tar")
        return extracted_file
    except KeyError:
        raise FileNotFoundError(f"File {filepath} not found in pod")


def _drain_stream_to_file(response, temp_file) -> None:
    had_data = True
    while response.is_open() or had_data:
        had_data = _drain_one_chunk(response, temp_file)

    # Ensure the temporary file is flushed and positioned for reading by callers.
    temp_file.flush()
    temp_file.seek(0)


def _drain_one_chunk(response, temp_file) -> bool:
    response.update(timeout=1)
    chunk = response.read_stdout()
    if chunk:
        temp_file.write(chunk)
    stderr = response.read_stderr()
    if stderr:
        raise FileNotFoundError(f"Error reading file: {stderr}")
    return bool(chunk)


class KubernetesRunner:
    """
    Runner that will execute commands inside the ox-connector Pod using the
    Kubernetes exec API.
    """

    pod_selector = "app.kubernetes.io/name=ox-connector"

    def __init__(self, deployment: "OxConnectorDeployment"):
        self.deployment = deployment
        self.v1 = client.CoreV1Api()
        self.namespace = deployment.namespace

    def _get_pod_name(self) -> str:
        pods = self.v1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=self.pod_selector,
            timeout_seconds=5,
        )
        for pod in pods.items:
            if pod.status.phase == "Running":
                return pod.metadata.name
        raise RuntimeError(
            f"No running pods found with selector '{self.pod_selector}' in namespace '{self.namespace}'",
        )

    def run(
        self,
        *args: typing.Union[str, typing.Sequence[str]],
        check: bool = True,
        capture_output: bool = False,
        text: bool = True,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        # Accept either run_command(["a","b",...]) or run_command("a","b",...)
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            cmd = [str(x) for x in args[0]]
        else:
            cmd = [str(x) for x in args]
        # Build safe shell string and append exit sentinel
        joined = " ".join(shlex.quote(s) for s in cmd)
        shell = f"{joined}; printf '\\n__EXIT_CODE__%d' $?"

        response = self.deployment.exec_stream(["sh", "-c", shell])

        stdout_bytes = bytearray()
        stderr_bytes = bytearray()
        had_data = True
        while response.is_open() or had_data:
            had_data = False
            response.update(timeout=1)
            chunk = response.read_stdout()
            if chunk:
                # stream returns bytes when binary=True
                stdout_bytes.extend(chunk)
                had_data = True
            err_chunk = response.read_stderr()
            if err_chunk:
                stderr_bytes.extend(err_chunk)
                had_data = True

        # Decode stdout for sentinel parsing and optional text output
        stdout_str = stdout_bytes.decode("utf-8", errors="replace")
        sentinel = "__EXIT_CODE__"
        exit_code = 0
        if sentinel in stdout_str:
            idx = stdout_str.rfind(sentinel)
            try:
                exit_code = int(stdout_str[idx + len(sentinel) :].strip())
            except Exception:
                exit_code = 1
            stdout_str = stdout_str[:idx].rstrip("\n")

        stdout_val = stdout_str if capture_output else None
        stderr_val = (
            stderr_bytes.decode("utf-8", errors="replace")
            if capture_output and stderr_bytes
            else None
        )

        if check and exit_code != 0:
            raise subprocess.CalledProcessError(
                exit_code,
                cmd,
                output=stdout_val,
            )

        if text:
            return subprocess.CompletedProcess(
                cmd,
                exit_code,
                stdout=stdout_val,
                stderr=stderr_val,
            )
        else:
            out_bytes = bytes(stdout_bytes) if stdout_bytes else None
            err_bytes = bytes(stderr_bytes) if stderr_bytes else None
            return subprocess.CompletedProcess(
                cmd,
                exit_code,
                stdout=out_bytes,
                stderr=err_bytes,
            )
