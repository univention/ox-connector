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

def create_resource(udm, name, domainname, context_id, ox_admin):
	dn = udm.create('oxresources/oxresources', 'cn=oxresources,cn=open-xchange', {
		'name': name,
		'displayname': name.upper(),
		'description': 'A description for {}'.format(name),
		'resourceMailAddress': '{}@{}'.format(name, domainname),
		'resourceadmin': str(ox_admin.properties['uidNumber']),
		'oxContextIDNum': context_id,
	})
	return dn

def test_add_resource_in_default_context(default_ox_context, new_resource_name, udm, domainname, ox_admin_udm_user):
	create_resource(udm, new_resource_name, domainname, None, ox_admin_udm_user)
	Resource = get_ox_integration_class('SOAP', 'Resource')
	cs = Resource.list(default_ox_context, pattern=new_resource_name)
	assert len(cs) == 1
	c = cs[0]
	assert c.display_name == new_resource_name.upper()
	assert c.description == 'A description for {}'.format(new_resource_name)
	assert c.email == '{}@{}'.format(new_resource_name, domainname)

def test_add_resource(new_context_id, new_resource_name, udm, ox_host, domainname, ox_admin_udm_user):
	create_context(udm, ox_host, new_context_id)
	create_resource(udm, new_resource_name, domainname, new_context_id, ox_admin_udm_user)
	Resource = get_ox_integration_class('SOAP', 'Resource')
	cs = Resource.list(new_context_id, pattern=new_resource_name)
	assert len(cs) == 1
	c = cs[0]
	assert c.display_name == new_resource_name.upper()
	assert c.description == 'A description for {}'.format(new_resource_name)
	assert c.email == '{}@{}'.format(new_resource_name, domainname)

def test_modify_resource(new_context_id, new_resource_name, udm, ox_host, domainname, ox_admin_udm_user):
	new_mail_address = '{}2@{}'.format(new_resource_name, domainname)
	create_context(udm, ox_host, new_context_id)
	dn = create_resource(udm, new_resource_name, domainname, new_context_id, ox_admin_udm_user)
	udm.modify('oxresources/oxresources', dn, {'description': None, 'displayname': 'New Display', 'resourceMailAddress': new_mail_address})
	Resource = get_ox_integration_class('SOAP', 'Resource')
	cs = Resource.list(new_context_id, pattern=new_resource_name)
	assert len(cs) == 1
	c = cs[0]
	assert c.display_name == 'New Display'
	assert c.email == new_mail_address
	assert c.description is None  # FIXME: fails...

def test_remove_resource(new_context_id, new_resource_name, udm, ox_host, domainname, ox_admin_udm_user):
	create_context(udm, ox_host, new_context_id)
	dn = create_resource(udm, new_resource_name, domainname, new_context_id, ox_admin_udm_user)
	udm.remove('oxresources/oxresources', dn)
	Resource = get_ox_integration_class('SOAP', 'Resource')
	cs = Resource.list(new_context_id, pattern=new_resource_name)
	assert len(cs) == 0
