#!/usr/local/bin/python

import os
import random
import string

DATA_DIR = '/var/lib/univention-appcenter/apps/ox-connector/data'
SERVER = '10.200.4.150'
DEFAULT_CONTEXT = 10
LOCAL_TIMEZONE = 'Europe/Berlin'
QUOTA = 32697
DOMAIN = 'intranet.ox.de'

def get_new_context_attributes(context_id):  # type: int -> Dict[str, str]
	name = 'context{}'.format(context_id)
	mapping = ['context{}'.format(context_id), str(context_id)]
	return {
		'id': context_id,
		'name': name,
		'mapping': mapping,
		'timezone': LOCAL_TIMEZONE,
		'username': get_context_admin_user(context_id),
		'displayname': 'OX Admin',
		'givenname': 'OX',
		'surname': 'Admin',
		'email': '{}@{}'.format(get_context_admin_user(context_id), DOMAIN),
		'quota': QUOTA,
		'password': get_random_password(),
	}

def get_random_password(length=15):  # type: (Optional[int]) -> str
	specials='@#$%&*-_+=:,.;?/()'
	pw = list()
	if length >= 4:
		pw.append(random.choice(string.lowercase))
		pw.append(random.choice(string.uppercase))
		pw.append(random.choice(string.digits))
		pw.append(random.choice(specials))
		length -= len(pw)
	pw.extend(random.choice(string.ascii_letters + string.digits + specials) for _x in range(length))
	random.shuffle(pw)
	return ''.join(pw)


def get_context_admin_user(context_id):  # type: (Union[int, str]) -> str
	if int(context_id) == DEFAULT_CONTEXT:
		return 'oxadmin'
	else:
		return 'oxadmin-context{}'.format(context_id)


def save_context_admin_password(context_id, password):
	context_admin_pwd_file = os.path.join(DATA_DIR, 'context{}.secret'.format(context_id))
	open(context_admin_pwd_file, 'w')
	os.chmod(0o600, context_admin_pwd_file)
	with open(context_admin_pwd_file, 'w') as fd:
		fd.write(password)


def get_context_admin_password(context_id):
	context_admin_pwd_file = os.path.join(DATA_DIR, 'context{}.secret'.format(context_id))
	with open(context_admin_pwd_file) as fd:
		return fd.read()
