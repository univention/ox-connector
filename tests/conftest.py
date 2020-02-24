import os
import time
from pathlib import Path

import pytest

from udm_rest import UDM

TEST_LOG_FILE = Path("/tmp/test.log")


@pytest.fixture(scope="session")
def truncate_wait_for_listener_log():
    def _func():
        with TEST_LOG_FILE.open("w"):
            pass

    yield _func

    TEST_LOG_FILE.unlink(missing_ok=True)


@pytest.fixture
def wait_for_listener(truncate_wait_for_listener_log):
    truncate_wait_for_listener_log()  # truncate before starting the test

    def _wait_for_dn(dn: str, timeout=10.0) -> None:
        start_time = time.time()
        with TEST_LOG_FILE.open("r") as fp:
            pos = fp.tell()
            while True:
                txt = fp.read()
                time_passed = time.time() - start_time
                if dn in txt:
                    print(
                        f"Listener_trigger finished handling {dn} after {time_passed:.1f} seconds."
                    )
                    # truncate, so this function can be used multiple times in the same test
                    truncate_wait_for_listener_log()
                    break
                if time_passed >= timeout:
                    print(
                        f"Listener_trigger did NOT handle {dn} for {timeout:.1f} seconds."
                    )
                    break
                pos_new = fp.tell()
                if pos == pos_new:
                    time.sleep(0.1)
                pos = pos_new

    return _wait_for_dn


def _new_id(cache):
    value = cache.get("newobjects/id", 100)
    value += 1
    cache.set("newobjects/id", value)
    return str(value)


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
def default_ox_context():
    return os.environ["DEFAULT_CONTEXT"]


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
    # cannot verify https in the container at the moment
    return "https://{}/univention/udm/".format(os.environ["LDAP_MASTER"])


@pytest.fixture
def udm_admin_username():
    return "Administrator"


@pytest.fixture
def udm_admin_password():
    return "univention"


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
        obj = mod.new(position="{},{}".format(position, self.ldap_base))
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

    def remove(self, module, dn):
        print("Removing {} from {}".format(dn, module))
        obj = self.client.get(module).get(dn)
        obj.delete()
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
        ]:
            if module_name in modules:
                modules.remove(module_name)
                modules.append(module_name)
        for module in modules:
            dns = _udm.new_objs[module]
            for dn in dns:
                _udm.remove(module, dn)
