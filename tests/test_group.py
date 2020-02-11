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

def create_user(udm, name, domainname, context_id):
	dn = udm.create('users/user', 'cn=users', {
		'username': name,
		'firstname': 'Emil',
		'lastname': name.title(),
		'password': 'univention',
		'mailPrimaryAddress': '{}@{}'.format(name, domainname),
		'isOxUser': True,
		'oxAccess': 'premium',
		'oxContext': context_id,
	}, wait_for_listener=False)
	return dn

def create_obj(udm, name, members):
	dn = udm.create('groups/group', 'cn=groups', {
		'name': name,
		'users': members,
		'isOxGroup': True,
	})
	return dn

def find_obj(context_id, name, assert_empty=False):
	Group = get_ox_integration_class('SOAP', 'Group')
	objs = Group.list(context_id, pattern=name)
	if assert_empty:
		assert len(objs) == 0
	else:
		assert len(objs) == 1
		obj = objs[0]
		print('Found', obj)
		return obj

def test_add_group_with_one_user(default_ox_context, new_user_name, new_group_name, udm, domainname):
	user_dn = create_user(udm, new_user_name, domainname, None)
	create_obj(udm, new_group_name, [user_dn])
	obj = find_obj(default_ox_context, new_group_name)
	assert obj.name == new_group_name
	assert len(obj.members) == 1

def test_add_group_with_multiple_users_and_contexts(new_context_id_generator, new_user_name_generator, new_group_name, udm, domainname):
	new_context_id = new_context_id_generator()
	user_dn1 = create_user(udm, new_user_name_generator(), domainname, new_context_id)
	new_context_id2 = new_context_id_generator()
	user_dn2 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
	user_dn3 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
	create_obj(udm, new_group_name, [user_dn1, user_dn2, user_dn3])
	obj = find_obj(new_context_id, new_group_name)
	assert obj.name == new_group_name
	assert len(obj.members) == 1
	obj2 = find_obj(new_context_id2, new_group_name)
	assert obj2.name == new_group_name
	assert len(obj2.members) == 2

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
