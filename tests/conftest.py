# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import logging
import os
import warnings
from pathlib import Path

import pytest

from univention.ox.soap.config import _CREDENTIALS

from udm_rest import UDM, UnprocessableEntity
from utils import FileUtility, FileLogs, SubprocessRunner

TEST_LOG_FILE = Path("/tmp/test.log")

log = logging.getLogger(__name__)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "skip_platform(platform): skip test for the given platform (ucs or k8s)",
    )


def pytest_addoption(parser):
    k8s_group = parser.getgroup("k8s", "Kubernetes related options")
    k8s_group.addoption(
        "--k8s",
        action="store_true",
        default=False,
        help="Enable Kubernetes-backed fixtures",
    )
    k8s_group.addoption(
        "--k8s-namespace",
        default=None,
        help="Override the kubeconfig default namespace",
    )
    k8s_group.addoption(
        "--k8s-logs-poll",
        action="store_true",
        default=False,
        help="Use polling for Kubernetes logs instead of streaming (workaround for fsnotify limits)",
    )
    parser.addoption(
        "--timeout",
        default=60,
        type=float,
        help="Timeout in seconds for the listener / consumer to process the changes. Defaults to 60 seconds.",
    )


@pytest.fixture(scope="session")
def file_utility(session_mocker, k8s_enabled, request):
    """
    File utility fixture.

    Use like:
        with file_utility.open(path) as fp:
            content = fp.read()
    """

    if not k8s_enabled:
        return FileUtility()

    deployment = request.getfixturevalue("k8s_ox_connector")
    from k8s_support import KubernetesFileUtility

    k8s_file_utility = KubernetesFileUtility(deployment)
    # NOTE: Some modules try to read files directly from the file system. Those
    # have to be mocked when running against a remote instance in Kubernetes.
    session_mocker.patch(
        'univention.ox.provisioning.accessprofiles.open',
        k8s_file_utility.open,
    )

    return k8s_file_utility


@pytest.fixture(scope="session")
def log_utility_session(k8s_enabled, request, pytestconfig):
    """
    Session-scoped log utility fixture.

    This fixture is mainly a supporting fixture for `log_utility`. In test
    cases typically the usage of `log_utility` is the right thing to do.

    The fixture is an instance of `BaseLogs`.
    """
    timeout = pytestconfig.getoption("--timeout")
    if not k8s_enabled:
        return FileLogs(timeout=timeout)

    deployment = request.getfixturevalue("k8s_ox_connector")
    from k8s_support import KubernetesLogs

    use_polling = pytestconfig.getoption("--k8s-logs-poll")
    return KubernetesLogs(deployment, use_polling=use_polling, timeout=timeout)


@pytest.fixture
def log_utility(log_utility_session):
    """
    Function-scoped log utility fixture.

    Provides a fresh log utility instance for each test by resetting the session-scoped
    log utility. Use this fixture to wait for log entries and manage log state in tests.

    Example:
        def test_something(log_utility):
            # Wait for a specific log entry
            log_utility.expect_log("some text", timeout=30.0)

            # Reset logs manually if needed
            log_utility.reset()

    Returns:
        BaseLogs: Log utility instance for the current test.
    """
    log_utility_session.reset()
    return log_utility_session


@pytest.fixture
def run_command(pytestconfig, k8s_enabled, request):
    """
    Fixture which supports running a command either locally or via the Kubernetes API.
    """
    if not k8s_enabled:
        return SubprocessRunner()

    from k8s_support import KubernetesRunner

    deployment = request.getfixturevalue("k8s_ox_connector")
    return KubernetesRunner(deployment)


@pytest.fixture(scope="session")
def truncate_wait_for_listener_log(log_utility_session):
    """
    Legacy fixture for log management.

    .. deprecated::

       Use `log_utility_session` fixture instead for better log handling capabilities.
    """
    warnings.warn(
        "truncate_wait_for_listener_log is deprecated. Use log_utility_session fixture instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    yield log_utility_session.reset
    log_utility_session.cleanup()


@pytest.fixture
def wait_for_listener(log_utility):
    """
    Legacy fixture for waiting for listener log entries.

    .. deprecated::

       Use `log_utility` fixture instead. Call `log_utility.expect_log` directly.
    """
    warnings.warn(
        "wait_for_listener is deprecated. Use log_utility fixture instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return log_utility.expect_dn


def _new_id(cache):
    value = cache.get(
        "newobjects/id",
        int(os.environ["DEFAULT_CONTEXT"]) + 100,
    )
    value += 1
    cache.set("newobjects/id", value)
    return value


@pytest.fixture
def new_context_id(cache):
    return _new_id(cache)


@pytest.fixture
def new_context_id_generator(cache):
    def f():
        return _new_id(cache)

    return f


@pytest.fixture
def new_resource_name(cache):
    value = _new_id(cache)
    return "room{}".format(value)


@pytest.fixture
def new_user_name(cache):
    value = _new_id(cache)
    return "user{}".format(value)


@pytest.fixture
def new_user_name_generator(cache):
    def f():
        value = _new_id(cache)
        return "user{}".format(value)

    return f


@pytest.fixture
def new_group_name(cache):
    value = _new_id(cache)
    return "group{}".format(value)


@pytest.fixture
def new_functional_account_name(cache):
    value = _new_id(cache)
    return "fa{}".format(value)


@pytest.fixture
def default_ox_context():
    return int(os.environ["DEFAULT_CONTEXT"])


@pytest.fixture
def domainname():
    return os.environ["DOMAINNAME"]


@pytest.fixture
def ldap_base():
    return os.environ["LDAP_BASE"]


@pytest.fixture
def default_imap_server():
    return os.environ["OX_IMAP_SERVER"]


@pytest.fixture
def udm_uri():
    # Use LDAP_MASTER in Jenkins UCS (where PORTAL_HOST isn't set).
    # Use PORTAL_HOST in other environments for UDM connection.
    # cannot verify https in the container at the moment
    return "https://{}/univention/udm/".format(
        os.getenv("LDAP_MASTER") or os.getenv("PORTAL_HOST"),
    )


@pytest.fixture
def umc_uri():
    return "https://{}/univention/".format(os.environ["LDAP_MASTER"])


@pytest.fixture
def udm_admin_username():
    return os.environ.get("TESTS_UDM_ADMIN_USERNAME", "Administrator")


@pytest.fixture
def udm_admin_password():
    return os.environ.get("TESTS_UDM_ADMIN_PASSWORD", "univention")


@pytest.fixture
def ox_host():
    return os.environ["OX_SOAP_SERVER"]


class UDMTest(object):
    def __init__(self, uri, ldap_base, username, password):
        self.client = UDM.http(uri, username, password)
        self.ldap_base = ldap_base
        self.new_objs = {}

    def create(self, module, position, attrs):
        print("Adding {} object in {}".format(module, position))
        mod = self.client.get(module)
        if position:
            obj = mod.new(position="{},{}".format(position, self.ldap_base))
        else:
            obj = mod.new(position=self.ldap_base)
        obj.properties.update(attrs)
        obj.save()
        dn = obj.dn
        print("Successfully added {}".format(dn))
        dns = self.new_objs.get(module, [])
        dns.append(dn)
        self.new_objs[module] = dns
        return dn

    def modify(self, module, dn, attrs):
        print("Modifying {} object {}".format(module, dn))
        obj = self.client.get(module).get(dn)
        obj.properties.update(attrs)
        obj.save()
        new_dn = obj.dn
        print("Successfully modified {}".format(dn))
        if new_dn != dn:
            dns = self.new_objs.get(module, [])
            try:
                dns.remove(dn)
            except ValueError:
                pass
            dns.append(new_dn)
            self.new_objs[module] = dns
        return new_dn

    def move(self, module, dn, position):
        print("Moving {} object {} into {}".format(module, dn, position))
        obj = self.client.get(module).get(dn)
        obj.position = position
        obj.save()
        new_dn = obj.dn
        print("Successfully moved {} to {}".format(dn, new_dn))
        dns = self.new_objs.get(module, [])
        try:
            dns.remove(dn)
        except ValueError:
            pass
        dns.append(new_dn)
        self.new_objs[module] = dns
        return new_dn

    def remove(self, module, dn, remove_from_new_objs=True):
        print("Removing {} from {}".format(dn, module))
        obj = self.client.get(module).get(dn)
        obj.delete()
        if remove_from_new_objs:
            dns = self.new_objs.get(module, [])
            try:
                dns.remove(dn)
            except ValueError:
                pass
            return dn

    def search(self, module, search_filter):
        return self.client.get(module).search(search_filter)


@pytest.fixture
def udm(udm_uri, ldap_base, udm_admin_username, udm_admin_password):
    _udm = UDMTest(udm_uri, ldap_base, udm_admin_username, udm_admin_password)
    yield _udm
    if _udm.new_objs:
        print("Test done. Now removing newly added DNs...")
        modules = list(_udm.new_objs.keys())
        for module_name in [
            "oxresources/oxresources",
            "groups/group",
            "users/user",
            "oxmail/oxcontext",
            "oxmail/accessprofile",
        ]:
            if module_name in modules:
                try:
                    modules.remove(module_name)
                except UnprocessableEntity:
                    pass

                modules.append(module_name)
        for module in modules:
            dns = _udm.new_objs[module]
            for dn in dns:
                try:
                    _udm.remove(module, dn, remove_from_new_objs=False)
                except UnprocessableEntity:
                    pass


@pytest.fixture
def create_ox_context(udm, new_context_id_generator, wait_for_listener):
    def _func(context_id=None):
        context_id = context_id or new_context_id_generator()
        dn = udm.create(
            "oxmail/oxcontext",
            "cn=open-xchange",
            {
                "oxQuota": 1000,
                "contextid": int(context_id),
                "name": "context{}".format(context_id),
            },
        )
        print("Created context", dn, "in UDM")
        _CREDENTIALS.clear()
        # Always wait for context to be created otherwise trying to access to context for
        # example by creating a object in the new context may crash the consumer.py with an auth error
        wait_for_listener(dn)
        return context_id

    return _func


@pytest.fixture
def get_udm_user(udm):
    def f(username):
        for user in udm.search("users/user", "uid={}".format(username)):
            return user.open()

    return f


@pytest.fixture
def create_ox_user(
    udm,
    get_udm_user,
    new_user_name_generator,
    domainname,
    default_ox_context,
    wait_for_listener,
):
    def _func(
        name=None,
        context_id=default_ox_context,
        enabled=True,
        wait=True,
        further_udm_attrs=None,
        ldap_path="cn=users",
    ):
        name = name or new_user_name_generator()
        attrs = {
            "username": name,
            "firstname": "Emil",
            "lastname": name.title(),
            "password": "univention",
            "mailPrimaryAddress": "{}@{}".format(name, domainname),
            "isOxUser": enabled,
            "oxAccess": "premium",
            "oxContext": context_id,
        }
        dn = udm.create(
            "users/user",
            ldap_path,
            attrs | (further_udm_attrs or {}),
        )
        print("Created user", dn, "in UDM")
        if wait:
            wait_for_listener(dn)
        return get_udm_user(name)

    return _func


@pytest.fixture
def create_ox_group(udm, wait_for_listener, default_ox_context):
    def _func(
        name,
        context_id=default_ox_context,
        members=None,
        enabled=True,
        wait=True,
    ):
        dn = udm.create(
            "groups/group",
            "cn=groups",
            {
                "name": name,
                "users": members,
                "isOxGroup": enabled,
                "oxContext": context_id,
            },
        )
        print(f"Created group {dn} in UDM")
        if wait:
            wait_for_listener(dn)

        return dn

    return _func


@pytest.fixture(scope="session")
def k8s(pytestconfig):
    """
    Session-scoped fixture that returns a Kubernetes helper object.
    """
    from k8s_support import KubernetesCluster, discover_namespace

    ns = pytestconfig.getoption("--k8s-namespace") or discover_namespace()
    return KubernetesCluster(namespace=ns)


@pytest.fixture(scope="session")
def k8s_enabled(pytestconfig):
    """
    Boolean fixture that reflects the --k8s CLI option for convenience.
    """
    return pytestconfig.getoption("--k8s")


@pytest.fixture(scope="session")
def k8s_ox_connector(k8s_enabled, request):
    """
    Returning an OxConnectorDeployment when Kubernetes is enabled.
    """
    if not k8s_enabled:
        return None
    k8s = request.getfixturevalue("k8s")
    from k8s_support import OxConnectorDeployment

    return OxConnectorDeployment(k8s)


@pytest.fixture(scope="session", autouse=True)
def k8s_check_environment(k8s_enabled):
    if not k8s_enabled:
        return

    # TODO:
    # Check if debug logging is enabled on the ox-connector pod, if not the tests will fail
    # the log line the k8s log utility is checking is only printed with debug logging

    mandatory_env_vars = [
        "OX_SOAP_SERVER",
        "OX_IMAP_SERVER",
        "DEFAULT_CONTEXT",
        "TESTS_UDM_ADMIN_USERNAME",
        "TESTS_UDM_ADMIN_PASSWORD",
        "LDAP_BASE",
        "DOMAINNAME",
        "PORTAL_HOST",
    ]

    for var in mandatory_env_vars:
        if var not in os.environ:
            raise ValueError(
                f"Env va '{var}' is required to run tests agains a k8s deployment",
            )


@pytest.fixture(scope="session", autouse=True)
def k8s_patch_ox_credentials_reader(session_mocker, request, k8s_enabled):
    if not k8s_enabled:
        return

    from k8s_support import K8sOXCredentialsReader

    deployment = request.getfixturevalue("k8s_ox_connector")
    reader = K8sOXCredentialsReader(deployment)
    log.info(
        "Patching univention.ox.soap.config._get_credentials to read from the Kubernetes Pod.",
    )
    session_mocker.patch("univention.ox.soap.config._get_credentials", reader)


@pytest.fixture
def platform(k8s_enabled):
    if k8s_enabled:
        return "k8s"
    else:
        return "ucs"


@pytest.fixture(autouse=True)
def skip_by_platform(request, platform):
    if request.node.get_closest_marker('skip_platform'):
        if (
            request.node.get_closest_marker('skip_platform').args[0]
            == platform
        ):
            pytest.skip('skipped on this platform: {}'.format(platform))
