# -*- coding: utf-8 -*-

# Copyright 2020 Univention GmbH
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

"""
Entry point for listener_trigger script.
"""

import traceback
import json

from univention.ox.backend_base import get_ox_integration_class
from univention.ox.soap.config import DEFAULT_CONTEXT, set_secrets_dir, set_soap_server
from .constants import DATA_DIR, NEW_FILES_DIR, OLD_FILES_DIR, OX_SOAP_SERVER


Context = get_ox_integration_class('SOAP', 'Context')
User = get_ox_integration_class('SOAP', 'User')

set_secrets_dir(DATA_DIR)
set_soap_server(OX_SOAP_SERVER)


def load_from_json_file(path):
	'''Just a helper function to get JSON content from a file, if it
	exists'''
	if not path.exists():
		return None
	with path.open() as fd:
		return json.load(fd)

class TriggerObject(object):
	'''A thin wrapper over a JSON file. Holds all the information from that
	file. May also hold information of this object from a previous run
	(needs a second, backup file for that)'''
	def __init__(self, entry_uuid, object_type, dn, attributes, options):
		self.entry_uuid = entry_uuid
		self.object_type = object_type
		self.dn = dn
		self.attributes = attributes
		self.options = options
		self.old_dn = None
		self.old_attributes = None
		self.old_options = None
		self._old_loaded = False

	def get_old_file_path(self):
		'''Name of the old file. May or may not be present. Is used by
		objects_from_files to move files if speceified.'''
		return OLD_FILES_DIR / '{}.json'.format(self.entry_uuid)

	def load_old(self):
		'''Loads the old filename and sets attributes accordingly'''
		old_path = self.get_old_file_path()
		content = load_from_json_file(old_path)
		if content is not None:
			self.old_dn = content['dn']
			self.old_attributes = content['object']
			self.old_options = content['options']
		self._old_loaded = True

	def was_added(self):
		'''Whether this object is new. Needs the have read an old file
		for this to give a meaningful response'''
		if self._old_loaded is False:
			return None
		return self.old_dn is None

	def was_modified(self):
		'''Whether this object was modified. Needs the have read an old
		file for this to give a meaningful response'''
		if self.was_deleted():
			return False
		if self._old_loaded is False:
			return None
		return not self.was_added() and not self.was_deleted()

	def was_deleted(self):
		'''Whether this object was deleted.'''
		return self.attributes is None

	def __repr__(self):
		if not self._old_loaded:
			return 'Object({}, {}, {})'.format(self.entry_uuid, self.object_type, self.dn)
		else:
			return 'Object({}, {}, {}, {})'.format(self.entry_uuid, self.object_type, self.dn, self.old_dn)

def objects_from_files(delete_files=True, move_files=False):
	'''Iterates over all JSON files and yields a TriggerObject. After the
	caller is done with it, it can delete or move the file. If it moves the
	file, a copy of this very JSON file is created so that a new run can
	reload it (useful if you need to act on various changes in
	attributes)'''
	for path in sorted(NEW_FILES_DIR.glob('*.json')):
		content = load_from_json_file(path)
		entry_uuid = content['id']
		object_type = content['udm_object_type']
		dn = content['dn']
		attributes = content['object']
		options = content['options']
		obj = TriggerObject(entry_uuid, object_type, dn, attributes, options)
		if move_files:
			obj.load_old()
		if obj.attributes is None and obj.old_attributes is None:
			# happens when creation and deletion happens within one
			# "listener cycle" => nothing happened
			pass
		else:
			yield obj
		if move_files:
			old_file_path = obj.get_old_file_path()
			old_file_path.parent.mkdir(parents=True, exist_ok=True)
			path.rename(old_file_path)
		elif delete_files:
			path.unlink()

def run_on_files(objs, f, stop_at_first_error=True):
	'''Iterate over objects (returned by objects_from_files) and runs a
	function f on this object. May continue to do so even if one iteration
	failed. Returns a reasonable exit code'''
	ret = 0
	for obj in objs:
		try:
			f(obj)
		except Exception:
			traceback.print_exc()
			ret = 1
			if stop_at_first_error:
				break
	return ret

# oxmail/oxcontext
# ================
def context_from_attributes(attributes):
	context = Context(id=attributes['contextid'])
	update_context(context, attributes)
	return context

def update_context(context, attributes):
	context.max_quota = attributes['oxQuota']
	context.name = attributes['name']

def context_exists(obj):
	if obj.attributes is None:
		# before delete
		context_id = obj.old_attributes['contextid']
	else:
		# before create
		context_id = obj.attributes['contextid']
	return bool(Context.list(pattern=context_id))

def create_context(obj):
	print('Creating', obj)
	if context_exists(obj):
		print(obj, 'exists. Modifying instead...')
		return modify_context(obj)
	context = context_from_attributes(obj.attributes)
	context.create()

def modify_context(obj):
	print('Modifying', obj)
	if obj.old_attributes:
		context = context_from_attributes(obj.old_attributes)
	else:
		print(obj, 'has no old data. Resync?')
		context = context_from_attributes(obj.attributes)
	update_context(context, obj.attributes)
	context.modify()

def delete_context(obj):
	print('Deleting', obj)
	if not context_exists(obj):
		print(obj, 'does not exist. Doing nothing...')
		return
	context = context_from_attributes(obj.old_attributes)
	context.remove()

# users/user
# ==========

def user_from_attributes(attributes):
	context_id = attributes.get('oxContext', DEFAULT_CONTEXT)
	user = User(context_id=context_id)
	update_user(user, attributes)
	return user

def update_user(user, attributes):
	#user.context_admin = context_admin,
	user.name = attributes['username'],
	user.display_name = attributes['oxDisplayName'],
	user.password = None,
	user.given_name = attributes['firstname'],
	user.sur_name = attributes['lastname'],
	user.primary_email = attributes['mailPrimaryAddress'],
	user.email1 = attributes['e-mail'],
	#user.aliases = attributes[],
	user.anniversary = attributes['oxAnniversary'],
	#user.assistant_name = attributes[],
	user.birthday = attributes['oxBirthday'],
	user.branches = attributes['oxBranches'],
	#user.business_category = attributes[],
	#user.categories = attributes[],
	#user.cellular_telephone1 = attributes[],
	#user.cellular_telephone2 = attributes[],
	user.city_business = attributes['city'],  # ???
	user.city_home = attributes['oxCityHome'],
	user.city_other = attributes['oxCityOther'],
	user.commercial_register = attributes['oxCommercialRegister'],
	#user.company = attributes[],
	user.country_business = attributes['oxCountryBusiness'],
	user.country_home = attributes['oxCountryHome'],
	user.country_other = attributes['oxCountryOther'],
	#user.drive_user_folder_mode = attributes[],
	#user.default_sender_address = attributes[],
	#user.default_group = attributes[],
	user.department = attributes['oxDepartment'],
	user.email2 = attributes['oxEmail2'],
	user.email3 = attributes['oxEmail3'],
	user.employee_type = attributes['employeeType'],  # ???
	user.fax_business = attributes['oxFaxBusiness'],
	user.fax_home = attributes['oxFaxHome'],
	user.fax_other = attributes['oxFaxOther'],
	#user.filestore_id = attributes[],
	#user.filestore_name = attributes[],
	#user.folder_tree = attributes[],
	#user.gui_preferences_for_soap = attributes[],
	#user.gui_spam_filter_enabled = attributes[],
	#user.imap_login = attributes[],
	#user.imap_port = attributes[],
	#user.imap_schema = attributes[],
	#user.imap_server = attributes[],
	#user.imap_server_string = attributes[],
	#user.info = attributes[],
	user.instant_messenger1 = attributes['oxInstantMessenger1'],
	user.instant_messenger2 = attributes['oxInstantMessenger2'],
	user.language = attributes['oxLanguage'],
	#user.mail_folder_confirmed_ham_name = attributes[],
	#user.mail_folder_confirmed_spam_name = attributes[],
	#user.mail_folder_drafts_name = attributes[],
	#user.mail_folder_sent_name = attributes[],
	#user.mail_folder_spam_name = attributes[],
	#user.mail_folder_trash_name = attributes[],
	#user.mail_folder_archive_full_name = attributes[],
	#user.mail_enabled = attributes[],
	user.manager_name = attributes['oxManagerName'],
	user.marital_status = attributes['oxMarialStatus'],
	#user.max_quota = attributes[],
	user.middle_name = attributes['oxMiddleName'],
	user.nickname = attributes['oxNickName'],
	user.note = attributes['oxNote'],
	user.number_of_children = attributes['oxNumOfChildren'],
	#user.number_of_employee = attributes[],
	#user.password_mech = attributes[],
	#user.password_expired = attributes[],
	user.position = attributes['oxPosition'],
	user.postal_code_business = attributes['postcode'],  # ???
	user.postal_code_home = attributes['oxPostalCodeHome'],
	user.postal_code_other = attributes['oxPostalCodeOther'],
	user.profession = attributes['oxProfession'],
	#user.room_number = attributes[],
	user.sales_volume = attributes['oxSalesVolume'],
	#user.smtp_port = attributes[],
	#user.smtp_schema = attributes[],
	#user.smtp_server = attributes[],
	#user.smtp_server_string = attributes[],
	user.spouse_name = attributes['oxSpouseName'],
	user.state_business = attributes['oxStateBusiness'],
	user.state_home = attributes['oxStateHome'],
	user.state_other = attributes['oxStateOther'],
	#user.street_business = attributes[],
	user.street_home = attributes['oxStreetHome'],
	user.street_other = attributes['oxStreetOther'],
	user.suffix = attributes['oxSuffix'],
	user.tax_id = attributes['oxTaxId'],
	user.telephone_assistant = attributes['oxTelephoneAssistant'],
	#user.telephone_business1 = attributes[],
	#user.telephone_business2 = attributes[],
	#user.telephone_callback = attributes[],
	user.telephone_car = attributes['oxTelephoneCar'],
	user.telephone_company = attributes['oxTelephoneCompany'],
	#user.telephone_home1 = attributes[],
	#user.telephone_home2 = attributes[],
	user.telephone_ip = attributes['oxTelephoneIp'],
	#user.telephone_isdn = attributes[],
	user.telephone_other = attributes['oxTelephoneOther'],
	#user.telephone_pager = attributes[],
	#user.telephone_primary = attributes[],
	#user.telephone_radio = attributes[],
	user.telephone_telex = attributes['oxTelephoneTelex'],
	user.telephone_ttytdd = attributes['oxTelephoneTtydd'],
	user.timezone = attributes['oxTimeZone'],
	user.title = attributes['title'],  # ???
	#user.upload_file_size_limit = attributes[],
	#user.upload_file_size_limitPerFile = attributes[],
	user.url = attributes['oxUrl'],
	#user.used_quota = attributes['oxUserQuota'], ???
	#user.user_attributes = attributes[],
	user.userfield01 = attributes['oxUserfield01'],
	user.userfield02 = attributes['oxUserfield02'],
	user.userfield03 = attributes['oxUserfield03'],
	user.userfield04 = attributes['oxUserfield04'],
	user.userfield05 = attributes['oxUserfield05'],
	user.userfield06 = attributes['oxUserfield06'],
	user.userfield07 = attributes['oxUserfield07'],
	user.userfield08 = attributes['oxUserfield08'],
	user.userfield09 = attributes['oxUserfield09'],
	user.userfield10 = attributes['oxUserfield10'],
	user.userfield11 = attributes['oxUserfield11'],
	user.userfield12 = attributes['oxUserfield12'],
	user.userfield13 = attributes['oxUserfield13'],
	user.userfield14 = attributes['oxUserfield14'],
	user.userfield15 = attributes['oxUserfield15'],
	user.userfield16 = attributes['oxUserfield16'],
	user.userfield17 = attributes['oxUserfield17'],
	user.userfield18 = attributes['oxUserfield18'],
	user.userfield19 = attributes['oxUserfield19'],
	user.userfield20 = attributes['oxUserfield20'],
	#user.primary_account_name = attributes[],
	#user.convert_drive_user_folders = attributes[],

def user_exists(obj):
	if obj.attributes is None:
		# before delete
		context_id = obj.old_attributes['contextid']
	else:
		# before create
		context_id = obj.attributes['contextid']
	return bool(User.list(pattern=context_id))

def create_user(obj):
	print('Creating', obj)
	if obj.attributes['isOxUser'] == 'Not':
		print(obj, 'is no OX user. Deleting instead...')
		return delete_user(obj)
	if user_exists(obj):
		print(obj, 'exists. Modifying instead...')
		return modify_user(obj)
	user = user_from_attributes(obj.attributes)
	user.create()

def modify_user(obj):
	print('Modifying', obj)
	if obj.old_attributes:
		if obj.old_attributes['isOxUser'] == 'Not':
			print(obj, 'was no OX user before. Creating instead')
			return create_user(obj)
		user = user_from_attributes(obj.old_attributes)
	else:
		print(obj, 'has no old data. Resync?')
		user = user_from_attributes(obj.attributes)
	update_user(user, obj.attributes)
	user.modify()

def delete_user(obj):
	print('Deleting', obj)
	if not user_exists(obj):
		print(obj, 'does not exist. Doing nothing...')
		return
	user = user_from_attributes(obj.old_attributes)
	user.remove()

def do(obj):
	'''This is your main function. Implement all your logic here'''
	if obj.object_type == 'oxmail/oxcontext':
		if obj.was_added():
			create_context(obj)
		elif obj.was_modified():
			modify_context(obj)
		elif obj.was_deleted():
			delete_context(obj)
	if obj.object_type == 'users/user':
		if obj.attributes['username'] == 'oxadmin':
			# FIXME
			return
		if obj.was_added():
			create_user(obj)
		elif obj.was_modified():
			modify_user(obj)
		elif obj.was_deleted():
			delete_user(obj)
