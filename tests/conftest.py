import os
import time

import pytest

from udm_rest import UDM


def _wait_for_listener():
    time.sleep(10)


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
def ox_admin_udm_user(udm):
    for obj in udm.search("users/user", "uid=oxadmin"):
        return obj.open()


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

    def create(self, module, position, attrs, wait_for_listener=True):
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
        if wait_for_listener:
            _wait_for_listener()
        return dn

    def modify(self, module, dn, attrs, wait_for_listener=True):
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
        if wait_for_listener:
            _wait_for_listener()
        return new_dn

    def remove(self, module, dn, wait_for_listener=True):
        print("Removing {} from {}".format(dn, module))
        obj = self.client.get(module).get(dn)
        obj.delete()
        dns = self.new_objs.get(module, [])
        try:
            dns.remove(dn)
        except ValueError:
            pass
        if wait_for_listener:
            _wait_for_listener()
        return dn

    def search(self, module, search_filter):
        return self.client.get(module).search(search_filter)


@pytest.fixture
def udm(udm_uri, ldap_base, udm_admin_username, udm_admin_password):
    _udm = UDMTest(udm_uri, ldap_base, udm_admin_username, udm_admin_password)
    yield _udm
    if _udm.new_objs:
        print("Test done. Now removing newly added DNs...")
        for module, dns in _udm.new_objs.items():
            for dn in dns:
                _udm.remove(module, dn, wait_for_listener=False)
        _wait_for_listener()
