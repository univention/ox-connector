# -*- coding: utf-8 -*-
#
# OX-UCS integration SOAP backend
#
# Copyright 2018 Univention GmbH
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

from .soap_config import save_context_admin_password, get_new_context_attributes, DEFAULT_CONTEXT
from .backend_base import BackendMetaClass, Context, Group, Resource, User, get_ox_integration_backend_class
from .credentials import ClientCredentials
from .services import get_ox_soap_service_class


__all__ = ['SoapContext', 'SoapGroup', 'SoapResource', 'SoapUser']


class SoapBackend(object):
	_backend = 'SOAP'
	_client_credential_objs = {}
	_service_objs = {}
	_base2soap = {}
	_mandatory_creation_attr = ()

	def __repr__(self):
		attrs = self._base2soap.keys() + ['id', 'name', 'context_id']
		return str(dict((k, getattr(self, k)) for k in attrs))

	def backend_init(self, *args, **kwargs):  # type: (*str, **str) -> None
		super(SoapBackend, self).backend_init(*args, **kwargs)
		self.context_id = int(kwargs.get('context_id') or self.context_id or DEFAULT_CONTEXT)
		self.default_service = self.service(DEFAULT_CONTEXT)
		self._soap_server = kwargs.pop('soap_server', '127.0.0.1')
		self._soap_username = kwargs.pop('soap_username', None)
		self._soap_password = kwargs.pop('soap_password', None)

	def kwargs2attr(self, **kwargs):  # type: (**str) -> None
		for k, v in kwargs.items():
			if k in self._base2soap or k in ('context_id', 'id', 'name'):
				setattr(self, k, v)
			elif k in ('soap_server', 'soap_username', 'soap_password'):
				# optional arguments for backend_init()
				pass
			else:
				self.logger.warn('Unknown argument {!r}={!r}.'.format(k, v))

	@classmethod
	def get_client_credentials(cls, context_id):  # type: (int) -> ClientCredentials
		if context_id not in cls._client_credential_objs:
			cls._client_credential_objs[context_id] = ClientCredentials(context_id=context_id)
		return cls._client_credential_objs[context_id]

	@classmethod
	def service(cls, context_id):  # type: () -> OxSoapService
		if context_id not in cls._service_objs.setdefault(cls._object_type, {}):
			OxSoapServiceClass = get_ox_soap_service_class(cls._object_type)  # type: Type[univention.ox.soap.services.OxSoapService]
			cls._service_objs[cls._object_type][context_id] = OxSoapServiceClass(cls.get_client_credentials(context_id))
		return cls._service_objs[cls._object_type][context_id]

	@classmethod
	def get_ox_soap_type_class(cls, object_type):  # type: (str) -> Type
		return get_ox_integration_backend_class(cls._backend, object_type)().default_service.Type

	@classmethod
	def from_ox(cls, context_id, obj_id=None, name=None):  # type: (int, Optional[int], Optional[str]) -> OxObject
		"""
		Load an object from OX.

		:param context_id: int - ID of context to get object from
		:param obj_id: int - ID of object to retrieve, either ID or name must be set
		:param name: str - name of object to retrieve, either ID or name must be set
		:return: OxObject
		"""
		soap_obj = cls.service(context_id).get_data(cls.service(context_id).Type(id=obj_id, name=name))
		return cls._soap_obj2base_obj(context_id, soap_obj)

	@classmethod
	def list(cls, context_id, pattern=None, *args, **kwargs):
		# type: (int, Optional[str], *str, **str) -> List[OxObject]
		"""
		Retrieve a list of context objects.

		:param context_id: int - ID of context to list object from
		:param pattern: str - pattern can be a string matching the ID or the
			name, use '*' not '.*' for placeholder. None to retrieve all
			contexts.
		:return: list of univention.ox.soap.types.Types.Context
		"""
		if pattern is None:
			soap_objs = cls.service(context_id).list_all()
		else:
			soap_objs = cls.service(context_id).list(pattern)
		return [cls._soap_obj2base_obj(context_id, soap_obj) for soap_obj in soap_objs]

	def create(self):  # type: () -> int
		"""
		Create object with current attributes.

		:return: int - ID of object in OX
		"""
		for attr in self._mandatory_creation_attr:
			assert getattr(self, attr) is not None, 'Mandatory attributes: {}.'.format(
				', '.join(self._mandatory_creation_attr))

		if hasattr(self, 'display_name'):
			self.display_name = self.name if self.display_name is None else self.display_name

		obj_kwargs = {'id': self.id, 'name': self.name}
		for base_attr, soap_attr in self._base2soap.items():
			value = getattr(self, base_attr)
			if value is not None:
				obj_kwargs[soap_attr] = value
		obj = self.service(self.context_id).Type(**obj_kwargs)
		new_obj = self.service(self.context_id).create(obj)
		self.logger.info('Created {} {!r} ({!r}).'.format(
			self._object_type.lower(), new_obj.name, int(obj.id) if obj.id else obj.id))
		return new_obj.id

	def modify(self):  # type: () -> None
		"""
		Modify object.

		Load the object from OX with from_ox(), change its attributes and then
		run modify().

		:return: None
		"""
		assert self.id is not None
		assert self.name is not None

		obj_kwargs = {'id': self.id, 'name': self.name}
		for base_attr, soap_attr in self._base2soap.items():
			obj_kwargs[soap_attr] = getattr(self, base_attr)
		obj = self.service(self.context_id).Type(**obj_kwargs)
		self.service(self.context_id).change(obj)
		self.logger.info('Modified {} {!r} ({!r}).'.format(
			self._object_type.lower(), obj.name, int(obj.id) if obj.id else obj.id))

	def remove(self):  # type: () -> None
		"""
		Delete object.

		:return: None
		"""
		assert self.id is not None or self.name is not None

		obj = self.service(self.context_id).Type(id=self.id, name=self.name)
		self.service(self.context_id).delete(obj)
		self.logger.info('Deleted {} {!r} ({!r}).'.format(
			self._object_type.lower(), obj.name, int(obj.id) if obj.id else obj.id))

	@classmethod
	def _soap_obj2base_obj(cls, context_id, soap_obj):  # type: (int, Any) -> OxObject
		kwargs = {'id': int(soap_obj.id), 'name': soap_obj.name, 'context_id': int(context_id)}
		for k, v in cls._base2soap.items():
			kwargs[k] = getattr(soap_obj, v)
		return cls(**kwargs)


class SoapContext(SoapBackend, Context):
	__metaclass__ = BackendMetaClass

	_base2soap = {
		'average_size': 'average_size',
		'enabled': 'enabled',
		'filestore_id': 'filestoreId',
		'filestore_name': 'filestore_name',
		'login_mappings': 'loginMappings',
		'max_quota': 'maxQuota',
		'read_database': 'readDatabase',
		'used_quota': 'usedQuota',
		'user_attributes': 'userAttributes',
		'write_database': 'writeDatabase',
	}
	_mandatory_creation_attr = ('id',)

	def backend_init(self, *args, **kwargs):  # type: (*str, **str) -> None
		super(SoapContext, self).backend_init(*args, **kwargs)
		self.context_id = int(kwargs.get('context_id') or kwargs.get('id') or self.context_id or DEFAULT_CONTEXT)

	def create(self):  # type: () -> int
		"""
		Create object with current attributes.

		:return: int - ID of object in OX
		"""
		assert self.id is not None

		context_creation_kwargs = get_new_context_attributes(self.id)
		self.name = self.name or context_creation_kwargs['name']
		self.max_quota = self.max_quota or context_creation_kwargs['quota']
		self.login_mappings = self.login_mappings or context_creation_kwargs['mapping']
		context_kwargs = {'id': self.id, 'name': self.name}
		for base_attr, soap_attr in self._base2soap.items():
			value = getattr(self, base_attr)
			if value is not None:
				context_kwargs[soap_attr] = value
		context = self.default_service.Type(**context_kwargs)
		admin_user = self.get_ox_soap_type_class('User')(
			name=context_creation_kwargs['username'],
			display_name=context_creation_kwargs['displayname'],
			password=context_creation_kwargs['password'],
			given_name=context_creation_kwargs['givenname'],
			sur_name=context_creation_kwargs['surname'],
			primaryEmail=context_creation_kwargs['email'],
			email1=context_creation_kwargs['email'],
			timezone=context_creation_kwargs['timezone']
		)
		self.logger.debug('Creating context: {!r}'.format(context))
		self.logger.debug('Creating context admin: {!r}'.format(admin_user))
		obj = self.default_service.create(context, admin_user)
		save_context_admin_password(context.id, admin_user.password)
		self.logger.info('Created context {!r} ({!r}).'.format(obj.name, int(obj.id) if obj.id else obj.id))
		return obj.id


	@classmethod
	def from_ox(cls, context_id=None, obj_id=None, name=None):  # type: (int, Optional[int], Optional[str]) -> OxObject
		"""
		Load context from OX.

		:param context_id: int - ID of context to retrieve, one of context_id, obj_id, name must be set
		:param obj_id: int - ID of context to retrieve, one of context_id, obj_id, name must be set
		:param name: str - name of context to retrieve, one of context_id, obj_id, name must be set
		:return: OxObject
		"""
		context_service = cls.service(DEFAULT_CONTEXT)
		context_obj = context_service.Type(id=context_id or obj_id, name=name)
		soap_obj = context_service.get_data(context_obj)
		return cls._soap_obj2base_obj(int(soap_obj.id), soap_obj)

	@classmethod
	def list(cls, context_id=None, pattern=None, *args, **kwargs):
		# type: (int, Optional[str], *str, **str) -> List[OxObject]
		"""
		Retrieve a list of context objects.

		:param context_id: int - ignored
		:param pattern: str - pattern can be a string matching the ID or the
			name, use '*' not '.*' for placeholder. None to retrieve all
			contexts.
		:return: list of univention.ox.soap.types.Types.Context
		"""
		context_service = cls.service(DEFAULT_CONTEXT)
		if pattern is None:
			soap_objs = context_service.list_all()
		else:
			soap_objs = context_service.list(pattern)
		return [cls._soap_obj2base_obj(int(soap_obj.id), soap_obj) for soap_obj in soap_objs]


class SoapGroup(SoapBackend, Group):
	__metaclass__ = BackendMetaClass

	_base2soap = {
		'display_name': 'displayname',
		'members': 'members',
	}
	_mandatory_creation_attr = ('name',)


class SoapResource(SoapBackend, Resource):
	__metaclass__ = BackendMetaClass

	_base2soap = {
		'available': 'available',
		'description': 'description',
		'display_name': 'displayname',
		'email': 'email',
	}
	_mandatory_creation_attr = ('name', 'email')


class SoapUser(SoapBackend, User):
	__metaclass__ = BackendMetaClass

	_base2soap = {
		'aliases': 'aliases',
		'anniversary': 'anniversary',
		'assistant_name': 'assistant_name',
		'birthday': 'birthday',
		'branches': 'branches',
		'business_category': 'business_category',
		'categories': 'categories',
		'cellular_telephone1': 'cellular_telephone1',
		'cellular_telephone2': 'cellular_telephone2',
		'city_business': 'city_business',
		'city_home': 'city_home',
		'city_other': 'city_other',
		'commercial_register': 'commercial_register',
		'company': 'company',
		'context_admin': 'contextadmin',
		'country_business': 'country_business',
		'country_home': 'country_home',
		'country_other': 'country_other',
		'drive_user_folder_mode': 'drive_user_folder_mode',
		'default_sender_address': 'defaultSenderAddress',
		'default_group': 'default_group',
		'department': 'department',
		'display_name': 'display_name',
		'email1': 'email1',
		'email2': 'email2',
		'email3': 'email3',
		'employee_type': 'employeeType',
		'fax_business': 'fax_business',
		'fax_home': 'fax_home',
		'fax_other': 'fax_other',
		'filestore_id': 'filestoreId',
		'filestore_name': 'filestore_name',
		'folder_tree': 'folderTree',
		'given_name': 'given_name',
		'gui_preferences_for_soap': 'guiPreferencesForSoap',
		'gui_spam_filter_enabled': 'gui_spam_filter_enabled',
		'imap_login': 'imapLogin',
		'imap_port': 'imapPort',
		'imap_schema': 'imapSchema',
		'imap_server': 'imapServer',
		'imap_server_string': 'imapServerString',
		'info': 'info',
		'instant_messenger1': 'instant_messenger1',
		'instant_messenger2': 'instant_messenger2',
		'language': 'language',
		'mail_folder_confirmed_ham_name': 'mail_folder_confirmed_ham_name',
		'mail_folder_confirmed_spam_name': 'mail_folder_confirmed_spam_name',
		'mail_folder_drafts_name': 'mail_folder_drafts_name',
		'mail_folder_sent_name': 'mail_folder_sent_name',
		'mail_folder_spam_name': 'mail_folder_spam_name',
		'mail_folder_trash_name': 'mail_folder_trash_name',
		'mail_folder_archive_full_name': 'mail_folder_archive_full_name',
		'mail_enabled': 'mailenabled',
		'manager_name': 'manager_name',
		'marital_status': 'marital_status',
		'max_quota': 'maxQuota',
		'middle_name': 'middle_name',
		'nickname': 'nickname',
		'note': 'note',
		'number_of_children': 'number_of_children',
		'number_of_employee': 'number_of_employee',
		'password': 'password',
		'password_mech': 'passwordMech',
		'password_expired': 'password_expired',
		'position': 'position',
		'postal_code_business': 'postal_code_business',
		'postal_code_home': 'postal_code_home',
		'postal_code_other': 'postal_code_other',
		'primary_email': 'primaryEmail',
		'profession': 'profession',
		'room_number': 'room_number',
		'sales_volume': 'sales_volume',
		'smtp_port': 'smtpPort',
		'smtp_schema': 'smtpSchema',
		'smtp_server': 'smtpServer',
		'smtp_server_string': 'smtpServerString',
		'spouse_name': 'spouse_name',
		'state_business': 'state_business',
		'state_home': 'state_home',
		'state_other': 'state_other',
		'street_business': 'street_business',
		'street_home': 'street_home',
		'street_other': 'street_other',
		'suffix': 'suffix',
		'sur_name': 'sur_name',
		'tax_id': 'tax_id',
		'telephone_assistant': 'telephone_assistant',
		'telephone_business1': 'telephone_business1',
		'telephone_business2': 'telephone_business2',
		'telephone_callback': 'telephone_callback',
		'telephone_car': 'telephone_car',
		'telephone_company': 'telephone_company',
		'telephone_home1': 'telephone_home1',
		'telephone_home2': 'telephone_home2',
		'telephone_ip': 'telephone_ip',
		'telephone_isdn': 'telephone_isdn',
		'telephone_other': 'telephone_other',
		'telephone_pager': 'telephone_pager',
		'telephone_primary': 'telephone_primary',
		'telephone_radio': 'telephone_radio',
		'telephone_telex': 'telephone_telex',
		'telephone_ttytdd': 'telephone_ttytdd',
		'timezone': 'timezone',
		'title': 'title',
		'upload_file_size_limit': 'uploadFileSizeLimit',
		'upload_file_size_limitPerFile': 'uploadFileSizeLimitPerFile',
		'url': 'url',
		'used_quota': 'usedQuota',
		'user_attributes': 'userAttributes',
		'userfield01': 'userfield01',
		'userfield02': 'userfield02',
		'userfield03': 'userfield03',
		'userfield04': 'userfield04',
		'userfield05': 'userfield05',
		'userfield06': 'userfield06',
		'userfield07': 'userfield07',
		'userfield08': 'userfield08',
		'userfield09': 'userfield09',
		'userfield10': 'userfield10',
		'userfield11': 'userfield11',
		'userfield12': 'userfield12',
		'userfield13': 'userfield13',
		'userfield14': 'userfield14',
		'userfield15': 'userfield15',
		'userfield16': 'userfield16',
		'userfield17': 'userfield17',
		'userfield18': 'userfield18',
		'userfield19': 'userfield19',
		'userfield20': 'userfield20',
		'primary_account_name': 'primaryAccountName',
		'convert_drive_user_folders': 'convert_drive_user_folders',
	}
	_mandatory_creation_attr = ('name', 'display_name', 'password', 'given_name', 'sur_name', 'primary_email', 'email1')

	def modify(self):  # type: () -> None
		"""
		Modify object.

		Load the object from OX with from_ox(), change its attributes and then
		run modify().

		:return: None
		"""
		if self.filestore_id == 0:
			self.filestore_id = None
		if not self.password:
			self.password_mech = None
		super(SoapUser, self).modify()

	def get_groups(self):  # type: (int) -> [Group]
		"""
		Retrieve groups the user is a member of.

		:return: list of Groups
		"""
		# SoapGroupService = get_ox_soap_service_class(SoapGroup._object_type)
		# group_service = SoapGroup.service
		user = self.service(self.context_id).Type(id=self.id, name=self.name)
		soap_objs = SoapGroup.service(self.context_id).list_groups_for_user(user)
		return [SoapGroup._soap_obj2base_obj(self.context_id, soap_obj) for soap_obj in soap_objs]
