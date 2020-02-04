#!/usr/bin/py.test

import time
import os

from univention.ox.backend_base import get_ox_integration_class
from udm_rest import UDM

import pytest

def wait_for_listener():
	time.sleep(10)

@pytest.fixture
def new_context_id(cache):
	value = cache.get('contexts/id', 100)
	value += 1
	cache.set('contexts/id', value)
	return str(value)

@pytest.fixture
def ldap_base():
	return os.environ['LDAP_BASE']

@pytest.fixture
def udm_uri():
	# cannot verify https in the container at the moment
	return 'http://{}/univention/udm/'.format(os.environ['LDAP_MASTER'])

@pytest.fixture
def udm_admin_username():
	return 'Administrator'

@pytest.fixture
def udm_admin_password():
	return 'univention'

@pytest.fixture
def ox_host():
	return os.environ['OX_SOAP_SERVER']

class UDMTest(object):
	def __init__(self, uri, ldap_base, username, password):
		self.client = UDM.http(uri, username, password)
		self.ldap_base = ldap_base
		self.new_objs = {}

	def create(self, module, position, attrs):
		print('Adding {} object in {}'.format(module, position))
		mod = self.client.get(module)
		obj = mod.new(position='{},{}'.format(position, self.ldap_base))
		obj.properties.update(attrs)
		obj.save()
		dn = obj.dn
		print('Successfully added {}'.format(dn))
		dns = self.new_objs.get(module, [])
		dns.append(dn)
		self.new_objs[module] = dns
		return dn

	def modify(self, module, dn, attrs):
		print('Modifying {} object {}'.format(module, dn))
		obj = self.client.get(module).get(dn)
		obj.properties.update(attrs)
		obj.save()
		new_dn = obj.dn
		print('Successfully modified {}'.format(dn))
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
		print('Removing {} from {}'.format(dn, module))
		obj = self.client.get(module).get(dn)
		obj.delete()
		dns = self.new_objs.get(module, [])
		try:
			dns.remove(dn)
		except ValueError:
			pass
		return dn

@pytest.fixture
def udm(udm_uri, ldap_base, udm_admin_username, udm_admin_password):
	_udm = UDMTest(udm_uri, ldap_base, udm_admin_username, udm_admin_password)
	yield _udm
	if _udm.new_objs:
		print('Test done. Now removing newly added DNs...')
		for module, dns in _udm.new_objs.items():
			for dn in dns:
				_udm.remove(module, dn)
		wait_for_listener()

def create_context(udm, ox_host, context_id):
	dn = udm.create('oxmail/oxcontext', 'cn=open-xchange', {
		'hostname': ox_host,
		'oxQuota': 1000,
		'oxDBServer': ox_host,
		'oxintegrationversion': '11.0.0-32A~4.4.0.201911191756',
		'contextid': context_id,
		'name': 'context{}'.format(context_id),
	})
	wait_for_listener()
	return dn

def test_add_context(new_context_id, udm, ox_host):
	create_context(udm, ox_host, new_context_id)
	Context = get_ox_integration_class('SOAP', 'Context')
	cs = Context.list(pattern=new_context_id)
	assert len(cs) == 1
	c = cs[0]
	assert c.name == 'context{}'.format(new_context_id)
	assert c.max_quota == 1000

def test_modify_context(new_context_id, udm, ox_host):
	dn = create_context(udm, ox_host, new_context_id)
	udm.modify('oxmail/oxcontext', dn, {'oxQuota': 2000})
	wait_for_listener()
	Context = get_ox_integration_class('SOAP', 'Context')
	cs = Context.list(pattern=new_context_id)
	assert len(cs) == 1
	c = cs[0]
	assert c.name == 'context{}'.format(new_context_id)
	assert c.max_quota == 2000

def test_remove_context(new_context_id, udm, ox_host):
	dn = create_context(udm, ox_host, new_context_id)
	udm.remove('oxmail/oxcontext', dn)
	wait_for_listener()
	Context = get_ox_integration_class('SOAP', 'Context')
	cs = Context.list(pattern=new_context_id)
	assert len(cs) == 0
