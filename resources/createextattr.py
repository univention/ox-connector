#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2019 Univention GmbH
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

import os.path
import csv
import sys
import subprocess
from univention.config_registry import ConfigRegistry

csvfilename = os.path.join(os.path.dirname(__file__), 'attrlist.csv')
if not os.path.exists(csvfilename):
	csvfilename = '/usr/share/univention-ox/attrlist.csv'
pwfilename = '/etc/ldap.secret'

ucr = ConfigRegistry()
ucr.load()
ldapbase = ucr['ldap/base']

from optparse import OptionParser

_parser = OptionParser()
_parser.add_option('--binddn', action='store', dest='binddn', help='ldap bind dn for UDM CLI operation')
_parser.add_option('--bindpwd', action='store', dest='bindpwd', help='ldap bind password for bind dn')
_parser.add_option('--bindpwdfile', action='store', dest='bindpwdfile', help='file with ldap bind password for bind dn')
(options, params) = _parser.parse_args()

if options.binddn:
	binddn = options.binddn
else:
	binddn = 'cn=admin,%s' % ldapbase

if options.bindpwd:
	bindpwd = options.bindpwd
else:
	fn = options.bindpwdfile or pwfilename
	with open(fn) as fp:
		bindpwd = fp.read().strip()

attrmap = csv.DictReader(open(csvfilename))

cmd_base = [
	'univention-directory-manager', 'settings/extended_attribute', 'create', '--binddn', binddn, '--bindpwd', bindpwd,
	'--ignore_exists', '--position', 'cn=open-xchange,cn=custom attributes,cn=univention,{}'.format(ldapbase),
]
for row in attrmap:
	cmd = list(cmd_base)
	cmd.extend([
		'--set', 'module={}'.format(row['module']),
		'--set', 'ldapMapping={}'.format(row['ldapMapping']),
		'--set', 'objectClass={}'.format(row['objectClass']),
		'--set', 'name={}'.format(row['name']),
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
		'--set', 'default={}'.format(row['default'] or ''),
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

	print('Installing extended attribute {}...'.format(row['name']))
	sys.stdout.flush()
	ret = subprocess.call(cmd)
	if ret:
		cmd_no_pw = [c if c != bindpwd else '********' for c in cmd]
		print('FAILED (exit {}) installing extended attribute {!r} with command:\n{!r}'.format(ret, row['name'], cmd_no_pw))
		sys.exit(ret)

print('All extended attribute were installed successfully.')
sys.exit(0)
