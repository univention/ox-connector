# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import dbm.gnu
import os
import time
import logging
from contextlib import contextmanager
from pathlib import Path

from univention.ox.provisioning.helpers import normalized_dn
import subprocess
import typing

log = logging.getLogger(__name__)

TEST_LOG_FILE = Path("/tmp/test.log")


class BaseLogs:
    """
    Base class of a Fixture to work with the logged output.
    """

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout

    def expect_log(
        self,
        text: str,
        *,
        timeout: typing.Optional[float] = None,
    ) -> None:
        """
        Expect the content of `text` to appear in the log.
        """
        if timeout is None:
            timeout = self.timeout
        raise NotImplementedError()

    def expect_dn(
        self,
        dn: str,
        *,
        timeout: typing.Optional[float] = None,
    ) -> None:
        """
        Normalize a distinguished name and expect it to appear in the log.
        """
        if timeout is None:
            timeout = self.timeout
        dn = normalized_dn(dn)
        return self.expect_log(dn, timeout=timeout)

    def reset(self) -> None:
        """
        Reset log buffer.

        This method ensures that a test is not influenced by logging output
        from previous tests.
        """
        raise NotImplementedError()

    def cleanup(self) -> None:
        """
        Hook to run cleanup at the end of the test session.

        The implementation is optional. The Hook is intended to allow files or
        similar resources to be cleaned up.
        """


class BaseFileUtility:
    """
    Base class of a Fixture to work with files needed by tests.
    """

    def open(self, path: typing.Union[os.PathLike, str], mode: str = "r"):
        raise NotImplementedError()

    @contextmanager
    def open_dbm(self, filepath: str, mode: str = "r"):
        """
        Convenience method to simplify reading from dbm files.
        """
        raise NotImplementedError()


class FileUtility(BaseFileUtility):
    """
    File-backed implementation.
    """

    @contextmanager
    def open(self, filepath: typing.Union[os.PathLike, str], mode: str = "r"):
        p = Path(filepath)
        if not p.is_absolute():
            raise ValueError(
                f"FileUtility only supports absolute paths: {filepath!r}",
            )
        with p.open(mode) as f:
            yield f

    @contextmanager
    def open_dbm(self, filepath: str, mode: str = "r"):
        p = Path(filepath)
        if not p.is_absolute():
            raise ValueError(
                f"FileUtility only supports absolute paths: {filepath!r}",
            )
        with dbm.gnu.open(str(p), mode) as db:
            yield db


class FileLogs(BaseLogs):
    """
    File-backed implementation.
    """

    def __init__(
        self,
        *,
        log_file: Path = TEST_LOG_FILE,
        timeout: float = 60.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.log_file = log_file

    def expect_log(
        self,
        text: str,
        *,
        timeout: typing.Optional[float] = None,
    ) -> None:
        if timeout is None:
            timeout = self.timeout
        start_time = time.time()
        with self.log_file.open("r") as fp:
            pos = fp.tell()
            while True:
                txt = fp.read()
                time_passed = time.time() - start_time
                if text in txt:
                    print(
                        f"Listener_trigger finished handling {text} after {time_passed:.1f} seconds.",
                    )
                    # truncate, so this function can be used multiple times in the same test
                    self.reset()
                    break
                if time_passed >= timeout:
                    raise AssertionError(
                        f"Listener_trigger did NOT handle {text} for {timeout:.1f} seconds.",
                    )
                    break
                pos_new = fp.tell()
                if pos == pos_new:
                    time.sleep(0.1)
                pos = pos_new
        time.sleep(1)

    def reset(self) -> None:
        log.debug("Truncating listener log file %s", self.log_file)
        with self.log_file.open("w"):
            pass

        try:
            # restore permissive mode to allow tests to write the file
            self.log_file.chmod(0o666)
        except Exception:
            log.debug(
                "Failed to chmod log file %s",
                self.log_file,
                exc_info=True,
            )

    def cleanup(self) -> None:
        log.debug("Removing listener log file %s", self.log_file)
        try:
            self.log_file.unlink(missing_ok=True)
        except Exception:
            log.debug(
                "Failed to remove log file %s",
                self.log_file,
                exc_info=True,
            )


class SubprocessRunner:
    """
    Encapsulates subprocess.run invocation so the implementation can be
    swapped later (e.g. with a Kubernetes-based runner). Instances are
    callable and behave like the previous _run function.
    """

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
        return subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=text,
            **kwargs,
        )
