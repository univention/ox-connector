#!/usr/bin/py.test

from univention.ox.backend_base import get_ox_integration_class

def create_context(udm, ox_host, context_id):
	dn = udm.create('oxmail/oxcontext', 'cn=open-xchange', {
		'hostname': ox_host,
		'oxQuota': 1000,
		'oxDBServer': ox_host,
		'oxintegrationversion': '11.0.0-32A~4.4.0.201911191756',
		'contextid': context_id,
		'name': 'context{}'.format(context_id),
	}, wait_for_listener=False)
	return dn

def create_obj(udm, name, domainname, context_id, ox_user=True):
	dn = udm.create('users/user', 'cn=users', {
		'username': name,
		'firstname': 'Emil',
		'lastname': name.title(),
		'password': 'univention',
		'mailPrimaryAddress': '{}@{}'.format(name, domainname),
		'isOxUser': ox_user,
		'oxAccess': 'premium',
		'oxContext': context_id,
	})
	return dn

def find_obj(context_id, name, assert_empty=False):
	User = get_ox_integration_class('SOAP', 'User')
	objs = User.list(context_id, pattern=name)
	if assert_empty:
		assert len(objs) == 0
	else:
		assert len(objs) == 1
		obj = objs[0]
		print('Found', obj)
		return obj

def test_ignore_user(default_ox_context, new_user_name, udm, domainname):
	create_obj(udm, new_user_name, domainname, None, ox_user=False)
	find_obj(default_ox_context, new_user_name, assert_empty=True)

def test_add_user_in_default_context(default_ox_context, new_user_name, udm, domainname):
	create_obj(udm, new_user_name, domainname, None)
	obj = find_obj(default_ox_context, new_user_name)
	assert obj.name == new_user_name
	assert obj.email1 == '{}@{}'.format(new_user_name, domainname)

def test_add_user(new_context_id, new_user_name, udm, ox_host, domainname):
	create_context(udm, ox_host, new_context_id)
	create_obj(udm, new_user_name, domainname, new_context_id)
	obj = find_obj(new_context_id, new_user_name)
	assert obj.name == new_user_name
	assert obj.email1 == '{}@{}'.format(new_user_name, domainname)

def test_modify_user(new_context_id, new_user_name, udm, ox_host, domainname):
	new_mail_address = '{}2@{}'.format(new_user_name, domainname)
	create_context(udm, ox_host, new_context_id)
	dn = create_obj(udm, new_user_name, domainname, new_context_id)
	udm.modify('users/user', dn, {'lastname': 'Newman', 'mailPrimaryAddress': new_mail_address, 'oxCommercialRegister': 'A register'})
	obj = find_obj(new_context_id, new_user_name)
	assert obj.email1 == new_mail_address
	assert obj.commercial_register == 'A register'
	assert obj.sur_name == 'Newman'

def test_remove_user(new_context_id, new_user_name, udm, ox_host, domainname):
	create_context(udm, ox_host, new_context_id)
	dn = create_obj(udm, new_user_name, domainname, new_context_id)
	udm.remove('users/user', dn)
	find_obj(new_context_id, new_user_name, assert_empty=True)

def test_remove_inactive_user(new_context_id, new_user_name, udm, ox_host, domainname):
	create_context(udm, ox_host, new_context_id)
	dn = create_obj(udm, new_user_name, domainname, new_context_id)
	find_obj(new_context_id, new_user_name)
	udm.modify('users/user', dn, {'isOxUser': False})
	find_obj(new_context_id, new_user_name, assert_empty=True)
