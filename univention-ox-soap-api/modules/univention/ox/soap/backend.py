# -*- coding: utf-8 -*-
#
# OX-UCS integration SOAP backend
#
# Copyright 2018-2020 Univention GmbH
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

from collections import namedtuple

from six import with_metaclass

from univention.ox.soap.backend_base import BackendMetaClass, Context, Group, Resource, SecondaryAccount, User, UserCopy, get_ox_integration_class

from .config import save_context_admin_password, remove_context_admin_password, get_new_context_attributes, DEFAULT_CONTEXT, OX_SOAP_SERVER, QUOTA
from .credentials import ClientCredentials
from .services import get_ox_soap_service_class


__all__ = ['SoapContext', 'SoapGroup', 'SoapResource', 'SoapUser', 'SoapAccount', 'SoapUserCopy']


SoapAttribute = namedtuple('SoapAttribute', ['name', 'default'], defaults=[None])


class SoapBackend(object):
    _backend = 'SOAP'
    _client_credential_objs = {}
    _service_objs = {}
    _base2soap = {}
    _mandatory_creation_attr = ()

    def __repr__(self):
        attrs = list(self._base2soap) + ['id', 'name', 'context_id']
        return str(dict((k, getattr(self, k)) for k in attrs))

    def backend_init(self, *args, **kwargs):  # type: (*str, **str) -> None
        super(SoapBackend, self).backend_init(*args, **kwargs)
        self.context_id = int(kwargs.get('context_id') or self.context_id or DEFAULT_CONTEXT)
        self.default_service = self.service(DEFAULT_CONTEXT)
        self._soap_server = kwargs.pop('soap_server', OX_SOAP_SERVER)
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

    def _base_obj2soap_obj(self):  # type: () -> Any
        """
        Creates a Soap Object from the OxObject
        """
        obj = {'id': self.id, 'name': self.name}
        for base_attr, soap_attr in self._base2soap.items():
            value = getattr(self, base_attr)
            if value is None:
                # we would want to set this to zeep.Nil to actually
                # remove this attribute via SOAP
                # but OX currently has a bug that ignores nil values
                # so we set string attributes to an empty string...
                # not correct, but the best we got
                value = soap_attr.default
            obj[soap_attr.name] = value
        return obj

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
        return get_ox_integration_class(cls._backend, object_type)().default_service.Type

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
        if soap_objs:
            soap_objs = cls.service(context_id).get_multiple_data(soap_objs)
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

        obj_kwargs = self._base_obj2soap_obj()
        obj = self.service(self.context_id).Type(**obj_kwargs)
        new_obj = self.service(self.context_id).create(obj)
        self.id = new_obj.id
        self.logger.info('Created {} {!r} in context {} (id={!r}).'.format(
            self._object_type.lower(), new_obj.name, self.context_id, self.id))
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

        obj_kwargs = self._base_obj2soap_obj()
        obj = self.service(self.context_id).Type(**obj_kwargs)
        self.service(self.context_id).change(obj)
        self.logger.info('Modified {} {!r} in context {} (id={!r}).'.format(
            self._object_type.lower(), obj.name, self.context_id, self.id))

    def remove(self):  # type: () -> None
        """
        Delete object.

        :return: None
        """
        assert self.id is not None or self.name is not None

        obj = self.service(self.context_id).Type(id=self.id, name=self.name)
        self.service(self.context_id).delete(obj)
        self.logger.info('Deleted {} {!r} in context {} (id={!r}).'.format(
            self._object_type.lower(), obj.name, self.context_id, self.id))

    @classmethod
    def _soap_obj2base_obj(cls, context_id, soap_obj):  # type: (int, Any) -> OxObject
        kwargs = {'id': int(soap_obj.id), 'name': soap_obj.name, 'context_id': int(context_id)}
        for k, v in cls._base2soap.items():
            kwargs[k] = getattr(soap_obj, v.name)
        return cls(**kwargs)


class SoapContext(with_metaclass(BackendMetaClass, SoapBackend, Context)):

    _base2soap = {
        'average_size': SoapAttribute('average_size'),
        'enabled': SoapAttribute('enabled'),
        'filestore_id': SoapAttribute('filestoreId'),
        'filestore_name': SoapAttribute('filestore_name'),
        'login_mappings': SoapAttribute('loginMappings'),
        'max_quota': SoapAttribute('maxQuota', QUOTA),
        'read_database': SoapAttribute('readDatabase'),
        'used_quota': SoapAttribute('usedQuota'),
        'user_attributes': SoapAttribute('userAttributes'),
        'write_database': SoapAttribute('writeDatabase'),
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
        context_kwargs = self._base_obj2soap_obj()
        context = self.default_service.Type(**context_kwargs)
        admin_user = self.get_ox_soap_type_class('User')(
            name=context_creation_kwargs['username'],
            display_name=context_creation_kwargs['displayname'],
            password=context_creation_kwargs['password'],
            given_name=context_creation_kwargs['givenname'],
            sur_name=context_creation_kwargs['surname'],
            primaryEmail=context_creation_kwargs['email'],
            email1=context_creation_kwargs['email'],
            timezone=context_creation_kwargs['timezone'],
        )
        self.logger.debug('Creating context: {!r}'.format(context))
        self.logger.debug('Creating context admin: {!r}'.format(admin_user))
        obj = self.default_service.create(context, admin_user)
        self.id = obj.id
        self.logger.info('Adding secret file for context {}'.format(self.id))
        save_context_admin_password(context.id, admin_user.name, admin_user.password)
        self.logger.info('Created context {!r} ({!r}).'.format(obj.name, self.id))
        return obj.id

    def remove(self):  # type: () -> None
        """
        Delete object.

        :return: None
        """
        super(SoapContext, self).remove()
        self.logger.info('Removing secret file for context {}'.format(self.id))
        remove_context_admin_password(self.id)

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


class SoapGroup(with_metaclass(BackendMetaClass, SoapBackend, Group)):

    _base2soap = {
        'display_name': SoapAttribute('displayname'),
        'members': SoapAttribute('members'),
    }
    _mandatory_creation_attr = ('name',)


class SoapResource(with_metaclass(BackendMetaClass, SoapBackend, Resource)):

    _base2soap = {
        'available': SoapAttribute('available'),
        'description': SoapAttribute('description', ''),
        'display_name': SoapAttribute('displayname'),
        'email': SoapAttribute('email'),
    }
    _mandatory_creation_attr = ('name', 'email')


class SoapUser(with_metaclass(BackendMetaClass, SoapBackend, User)):

    _base2soap = {
        'aliases': SoapAttribute('aliases'),
        'anniversary': SoapAttribute('anniversary'),
        'assistant_name': SoapAttribute('assistant_name'),
        'birthday': SoapAttribute('birthday'),
        'branches': SoapAttribute('branches', ''),
        'business_category': SoapAttribute('business_category'),
        'categories': SoapAttribute('categories'),
        'cellular_telephone1': SoapAttribute('cellular_telephone1', ''),
        'cellular_telephone2': SoapAttribute('cellular_telephone2', ''),
        'city_business': SoapAttribute('city_business', ''),
        'city_home': SoapAttribute('city_home', ''),
        'city_other': SoapAttribute('city_other', ''),
        'commercial_register': SoapAttribute('commercial_register', ''),
        'company': SoapAttribute('company', ''),
        'context_admin': SoapAttribute('contextadmin'),
        'country_business': SoapAttribute('country_business', ''),
        'country_home': SoapAttribute('country_home', ''),
        'country_other': SoapAttribute('country_other', ''),
        'drive_user_folder_mode': SoapAttribute('drive_user_folder_mode'),
        'default_sender_address': SoapAttribute('defaultSenderAddress'),
        'default_group': SoapAttribute('default_group'),
        'department': SoapAttribute('department', ''),
        'display_name': SoapAttribute('display_name', ''),
        'email1': SoapAttribute('email1', ''),
        'email2': SoapAttribute('email2', ''),
        'email3': SoapAttribute('email3', ''),
        'employee_type': SoapAttribute('employeeType'),
        'fax_business': SoapAttribute('fax_business', ''),
        'fax_home': SoapAttribute('fax_home', ''),
        'fax_other': SoapAttribute('fax_other', ''),
        'filestore_id': SoapAttribute('filestoreId'),
        'filestore_name': SoapAttribute('filestore_name'),
        'folder_tree': SoapAttribute('folderTree'),
        'given_name': SoapAttribute('given_name', ''),
        'gui_preferences_for_soap': SoapAttribute('guiPreferencesForSoap'),
        'gui_spam_filter_enabled': SoapAttribute('gui_spam_filter_enabled'),
        'imap_login': SoapAttribute('imapLogin', ''),
        'imap_port': SoapAttribute('imapPort'),
        'imap_schema': SoapAttribute('imapSchema'),
        'imap_server': SoapAttribute('imapServer'),
        'imap_server_string': SoapAttribute('imapServerString'),
        'info': SoapAttribute('info'),
        'instant_messenger1': SoapAttribute('instant_messenger1', ''),
        'instant_messenger2': SoapAttribute('instant_messenger2', ''),
        'language': SoapAttribute('language'),
        'mail_folder_confirmed_ham_name': SoapAttribute('mail_folder_confirmed_ham_name'),
        'mail_folder_confirmed_spam_name': SoapAttribute('mail_folder_confirmed_spam_name'),
        'mail_folder_drafts_name': SoapAttribute('mail_folder_drafts_name'),
        'mail_folder_sent_name': SoapAttribute('mail_folder_sent_name'),
        'mail_folder_spam_name': SoapAttribute('mail_folder_spam_name'),
        'mail_folder_trash_name': SoapAttribute('mail_folder_trash_name'),
        'mail_folder_archive_full_name': SoapAttribute('mail_folder_archive_full_name'),
        'mail_enabled': SoapAttribute('mailenabled'),
        'manager_name': SoapAttribute('manager_name', ''),
        'marital_status': SoapAttribute('marital_status', ''),
        'max_quota': SoapAttribute('maxQuota'),
        'middle_name': SoapAttribute('middle_name', ''),
        'nickname': SoapAttribute('nickname', ''),
        'note': SoapAttribute('note', ''),
        'number_of_children': SoapAttribute('number_of_children', ''),
        'number_of_employee': SoapAttribute('number_of_employee', ''),
        'password': SoapAttribute('password'),
        'password_mech': SoapAttribute('passwordMech'),
        'password_expired': SoapAttribute('password_expired'),
        'position': SoapAttribute('position', ''),
        'postal_code_business': SoapAttribute('postal_code_business', ''),
        'postal_code_home': SoapAttribute('postal_code_home', ''),
        'postal_code_other': SoapAttribute('postal_code_other', ''),
        'primary_email': SoapAttribute('primaryEmail', ''),
        'profession': SoapAttribute('profession', ''),
        'room_number': SoapAttribute('room_number', ''),
        'sales_volume': SoapAttribute('sales_volume', ''),
        'smtp_port': SoapAttribute('smtpPort'),
        'smtp_schema': SoapAttribute('smtpSchema'),
        'smtp_server': SoapAttribute('smtpServer'),
        'smtp_server_string': SoapAttribute('smtpServerString'),
        'spouse_name': SoapAttribute('spouse_name', ''),
        'state_business': SoapAttribute('state_business', ''),
        'state_home': SoapAttribute('state_home', ''),
        'state_other': SoapAttribute('state_other', ''),
        'street_business': SoapAttribute('street_business', ''),
        'street_home': SoapAttribute('street_home', ''),
        'street_other': SoapAttribute('street_other', ''),
        'suffix': SoapAttribute('suffix', ''),
        'sur_name': SoapAttribute('sur_name', ''),
        'tax_id': SoapAttribute('tax_id', ''),
        'telephone_assistant': SoapAttribute('telephone_assistant', ''),
        'telephone_business1': SoapAttribute('telephone_business1', ''),
        'telephone_business2': SoapAttribute('telephone_business2', ''),
        'telephone_callback': SoapAttribute('telephone_callback'),
        'telephone_car': SoapAttribute('telephone_car', ''),
        'telephone_company': SoapAttribute('telephone_company', ''),
        'telephone_home1': SoapAttribute('telephone_home1', ''),
        'telephone_home2': SoapAttribute('telephone_home2', ''),
        'telephone_ip': SoapAttribute('telephone_ip', ''),
        'telephone_isdn': SoapAttribute('telephone_isdn'),
        'telephone_other': SoapAttribute('telephone_other', ''),
        'telephone_pager': SoapAttribute('telephone_pager', ''),
        'telephone_primary': SoapAttribute('telephone_primary'),
        'telephone_radio': SoapAttribute('telephone_radio'),
        'telephone_telex': SoapAttribute('telephone_telex', ''),
        'telephone_ttytdd': SoapAttribute('telephone_ttytdd', ''),
        'timezone': SoapAttribute('timezone'),
        'title': SoapAttribute('title', ''),
        'upload_file_size_limit': SoapAttribute('uploadFileSizeLimit'),
        'upload_file_size_limitPerFile': SoapAttribute('uploadFileSizeLimitPerFile'),
        'url': SoapAttribute('url', ''),
        'used_quota': SoapAttribute('usedQuota'),
        'user_attributes': SoapAttribute('userAttributes'),
        'userfield01': SoapAttribute('userfield01', ''),
        'userfield02': SoapAttribute('userfield02', ''),
        'userfield03': SoapAttribute('userfield03', ''),
        'userfield04': SoapAttribute('userfield04', ''),
        'userfield05': SoapAttribute('userfield05', ''),
        'userfield06': SoapAttribute('userfield06', ''),
        'userfield07': SoapAttribute('userfield07', ''),
        'userfield08': SoapAttribute('userfield08', ''),
        'userfield09': SoapAttribute('userfield09', ''),
        'userfield10': SoapAttribute('userfield10', ''),
        'userfield11': SoapAttribute('userfield11', ''),
        'userfield12': SoapAttribute('userfield12', ''),
        'userfield13': SoapAttribute('userfield13', ''),
        'userfield14': SoapAttribute('userfield14', ''),
        'userfield15': SoapAttribute('userfield15', ''),
        'userfield16': SoapAttribute('userfield16', ''),
        'userfield17': SoapAttribute('userfield17', ''),
        'userfield18': SoapAttribute('userfield18', ''),
        'userfield19': SoapAttribute('userfield19', ''),
        'userfield20': SoapAttribute('userfield20', ''),
        'primary_account_name': SoapAttribute('primaryAccountName'),
        'convert_drive_user_folders': SoapAttribute('convert_drive_user_folders'),
        'image1': SoapAttribute('image1'),
        'image1ContentType': SoapAttribute('image1ContentType', ''),
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


class SoapSecondaryAccount(with_metaclass(BackendMetaClass, SoapBackend, SecondaryAccount)):
    _base2soap = {
        'email': SoapAttribute('primaryAddress'),
        'personal': SoapAttribute('personal'),
        'login': SoapAttribute('login'),
        'mail_endpoint_source': SoapAttribute('mailEndpointSource'),
        'users': SoapAttribute('users'),
        'groups': SoapAttribute('groups'),
    }
    _mandatory_creation_attr = ('name', 'email')

    @classmethod
    def from_ox(cls, context_id, obj_id=None, name=None):  # type: (int, Optional[int], Optional[str])
        raise NotImplementedError()

    @classmethod
    def list(cls, context_id, pattern=None, *args, **kwargs):
        return cls.service(context_id).list()

    def create(self):
        """
        Create object with current attributes.
        """
        obj = self.service(self.context_id).Type(name=self.name, primaryAddress=self.email, personal=self.personal, mailEndpointSource=self.mail_endpoint_source, login=self.login)
        self.service(self.context_id).create(obj, self.users, self.groups)
        self.logger.info('Created {} {!r} in context {} (id={!r}).'.format(
            self._object_type.lower(), obj.name, self.context_id, self.email))

    def modify(self):
        raise NotImplementedError()

    def remove(self):
        """
        Delete object.

        :return: None
        """
        obj = self.service(self.context_id).Type(primaryAddress=self.email)
        self.service(self.context_id).delete(obj.primaryAddress)
        self.logger.info('Deleted {} {!r} in context {} (id={!r}).'.format(
            self._object_type.lower(), obj.name, self.context_id, self.email))


class SoapUserCopy(with_metaclass(BackendMetaClass, SoapBackend, UserCopy)):

    _base2soap = {}
    _mandatory_creation_attr = ()
