#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2022 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.

import csv
import os.path
import sys
import subprocess
from optparse import OptionParser
from univention.config_registry import ConfigRegistry
try:
	from typing import List
except ImportError:
	pass


EXT_ATTR_CSV_PATH = os.path.join(os.path.dirname(__file__), 'attrlist.csv')
if not os.path.exists(EXT_ATTR_CSV_PATH):
	EXT_ATTR_CSV_PATH = '/usr/share/univention-ox/attrlist.csv'
CN_ADMIN_SECRET_PATH = '/etc/ldap.secret'
_EXT_ATTR_CONTAINER = 'cn=open-xchange,cn=custom attributes,cn=univention'

ucr = ConfigRegistry()
ucr.load()
ldapbase = ucr['ldap/base']
ext_attr_container_dn = '{},{}'.format(_EXT_ATTR_CONTAINER, ldapbase)


_parser = OptionParser()
_parser.add_option('--binddn', action='store', dest='binddn', help='ldap bind dn for UDM CLI operation')
_parser.add_option('--bindpwdfile', action='store', dest='bindpwdfile', help='file with ldap bind password for bind dn')
_parser.add_option(
	'--update', action='store_true', dest='update', default=False,
	help='update existing extended attributes with the package defaults (except "default" property)'
)
_parser.add_option(
	'--update-reset-defaults', action='store_true', dest='update_defaults', default=False,
	help='update existing extended attributes with the package defaults (including "default" property)'
)
(options, params) = _parser.parse_args()

if options.update_defaults:
	options.update = True

if options.binddn:
	binddn = options.binddn
else:
	binddn = 'cn=admin,{}'.format(ldapbase)


def run_ext(attr_name, cmd):  # type: (str, List[str]) -> None
	ret = subprocess.call(cmd)
	if ret:
		print('FAILED (exit {}) {} extended attribute {!r} with command:\n{!r}'.format(
			ret, 'updating' if options.update else 'installing', attr_name, cmd)
		)
		sys.exit(ret)


cmd_base = [
	'univention-directory-manager', 'settings/extended_attribute',
	'modify' if options.update else 'create',
]

if ucr['server/role'] != 'domaincontroller_master':
    cmd_base += ['--binddn', binddn, '--bindpwdfile', options.bindpwdfile]

if not options.update:
	cmd_base.extend([
		'--ignore_exists',
		'--position', ext_attr_container_dn,
	])

attrmap = csv.DictReader(open(EXT_ATTR_CSV_PATH, 'r'))
for row in attrmap:
	cmd = list(cmd_base)
	if options.update:
		cmd.extend(['--dn', 'cn={},{}'.format(row['name'], ext_attr_container_dn)])
		if options.update_defaults:
			cmd.extend(['--set', 'default={}'.format(row['default'] or '')])
		# else: keep previous 'default' property setting
	else:
		cmd.extend([
			'--set', 'name={}'.format(row['name']),
			'--set', 'default={}'.format(row['default'] or ''),
		])
	cmd.extend([
		'--set', 'module={}'.format(row['module']),
		'--set', 'ldapMapping={}'.format(row['ldapMapping']),
		'--set', 'objectClass={}'.format(row['objectClass']),
		'--set', 'shortDescription={}'.format(row['shortDescription'] or ''),
		'--set', 'longDescription={}'.format(row['longDescription'] or ''),
		'--set', 'translationShortDescription="de_DE" "{}"'.format(row['translationShortDescription'] or ''),
		'--set', 'translationLongDescription="de_DE" "{}"'.format(row['translationLongDescription'] or ''),
		'--set', 'tabName={}'.format(row['tabName'] or ''),
		'--set', 'translationTabName="de_DE" "{}"'.format(row['translationTabName'] or ''),
		'--set', 'overwriteTab={}'.format(row['overwriteTab'] or ''),
		'--set', 'valueRequired={}'.format(row['valueRequired'] or ''),
		'--set', 'CLIName={}'.format(row['CLIName'] or ''),
		'--set', 'syntax={}'.format(row['syntax'] or ''),
		'--set', 'tabAdvanced={}'.format(row['tabAdvanced'] or ''),
		'--set', 'mayChange={}'.format(row['mayChange'] or ''),
		'--set', 'multivalue={}'.format(row['multivalue'] or ''),
		'--set', 'deleteObjectClass={}'.format(row['deleteObjectClass'] or ''),
		'--set', 'tabPosition={}'.format(row['tabPosition'] or ''),
		'--set', 'overwritePosition={}'.format(row['overwritePosition'] or ''),
		'--set', 'doNotSearch={}'.format(row['doNotSearch'] or ''),
		'--set', 'hook={}'.format(row['hook'] or ''),
	])
	if row.get("translationGroupName"):
		cmd.extend(['--set', 'translationGroupName="de_DE" "{}"'.format(row['translationGroupName'])])
	for propertyName in ('groupName', 'groupPosition', 'disableUDMWeb'):
		if row.get(propertyName):
			cmd.extend(['--set', '{}={}'.format(propertyName, row[propertyName])])

	print('{} extended attribute {}...'.format('Updating' if options.update else 'Installing', row['name']))
	sys.stdout.flush()
	run_ext(row['name'], cmd)

print('All extended attribute were {} successfully.'.format('updated' if options.update else 'installed'))

sys.exit(0)
