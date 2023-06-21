# -*- coding: utf-8 -*-
#
# OX-UCS integration backend base class
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

import logging
try:
    from typing import Dict, List, Optional, Type, Union
    import datetime
except ImportError:
    pass

from .config import OX_APPSUITE_MAJOR_VERSION

__ox_integration_backend_class_registry = dict()  # type: Dict[str, Dict[str, Type["OxObject"]]]
__ox_integration_backend_object_cache = {}  # type: Dict[str, Dict[str, "OxObject"]]


def register_ox_integration_backend_class(backend, object_type, cls):
    # type: (str, str, Type["OxObject"]) -> None
    """
    Backend class registration. Used by BackendMetaClass.

    :param backend: str - either 'CSV' or 'SOAP'
    :param object_type: str - one of 'Context', 'Group', 'Resource', 'User', 'Account'
    :param cls: Type - the class that should be registered (a subclass of OxObject or one)
    :return: None
    """
    __ox_integration_backend_class_registry.setdefault(backend, {})[object_type] = cls


def get_ox_integration_class(backend, object_type):  # type: (str, str) -> Type["OxObject"]
    """
    Get a class implementing OX object manipulation.

    :param backend: str - either 'CSV' or 'SOAP'
    :param object_type: str - one of 'Context', 'Group', 'Resource', 'User', 'Account'
    :return: Type - a subclass of OxObject
    """
    if backend == 'SOAP':
        import univention.ox.soap.backend  # load meta classes
    return __ox_integration_backend_class_registry.get(backend, {}).get(object_type)


class BackendMetaClass(type):
    """
    Meta class for ox integration backend classes. All concrete classes should
    use this as a metaclass to automatically register themselves.
    """
    logger = logging.getLogger(__name__)

    def __new__(cls, clsname, bases, attrs):
        kls = super(BackendMetaClass, cls).__new__(cls, clsname, bases, attrs)  # type: Type["OxObject"]
        if issubclass(kls, OxObject) and getattr(kls, '_backend') and getattr(kls, '_object_type'):
            if not kls.logger:
                kls.logger = cls.logger.getChild(clsname)
            register_ox_integration_backend_class(kls._backend, kls._object_type, kls)
            cls.logger.debug('Registered class {!r} of backend {!r} for object type {!r}.'.format(
                cls.__name__, kls._backend, kls._object_type))
        return kls


class OxObject(object):
    """
    Base of OX object manipulation classes. Do not derive your backend
    implementation from this, but from one of its decedents (Context, Group
    Resource, User, Account).

    Both `id` and `name` are sufficient to identify an OX object in a context.
    `context_id` must be set (except for Context, where it's the same as `id`).
    """
    _backend = None  # type: str
    _object_type = None  # type: str

    id = None  # type: int
    name = None  # type: str
    context_id = None  # type: int

    def __init__(self, *args, **kwargs):  # type: (*str, **str) -> None
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.kwargs2attr(**kwargs)
        self.backend_init(*args, **kwargs)

    def backend_init(self, *args, **kwargs):  # type: (*str, **str) -> None
        pass

    def kwargs2attr(self, **kwargs):  # type: (**str) -> None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def create(self):  # type: () -> int
        """
        Create object with current attributes.

        :return: int - ID of object in OX
        """
        raise NotImplementedError()

    def modify(self):  # type: () -> None
        """
        Modify object.

        Load the object from OX with from_ox(), change its attributes and then
        run modify().

        :return: None
        """
        raise NotImplementedError()

    def remove(self):  # type: () -> None
        """
        Delete object.

        :return: None
        """
        raise NotImplementedError()

    def from_ox(self, context_id, obj_id=None, name=None):
        # type: (int, Optional[int], Optional[str]) -> "OxObject"
        """
        Load an object from OX.

        :param context_id: int - ID of context to get object from
        :param obj_id: int - ID of object to retrieve, either ID or name must be set
        :param name: str - name of object to retrieve, either ID or name must be set
        :return: OxObject
        """
        raise NotImplementedError()

    def list(self, context_id, pattern, *args, **kwargs):
        # type: (int, str, *str, **str) -> ["OxObject"]
        """
        Retrieve a list of objects.

        :param context_id: int - ID of context to list object from
        :param pattern: str - pattern can be a string matching the ID or the
            name, use '*' not '.*' for placeholder. None to retrieve all
            objects.
        :return: list of OxObjects
        """
        raise NotImplementedError()


class Context(OxObject):
    """
    Representation of a OX context.

    When implementing a class derived from this, use BackendMetaClass as its
    metaclass.
    """
    _object_type = 'Context'

    average_size = None  # type: int
    enabled = True
    filestore_id = None  # type: int
    filestore_name = None  # type: str
    login_mappings = []  # type: List[str]
    max_quota = None  # type: int
    read_database = None  # type: Dict[str, str]
    used_quota = None  # type: int
    user_attributes = None  # type: Dict[str, Dict[str, Union[str, Dict[str, str]]]]
    write_database = None  # type: Dict[str, str]

    def __init__(self, *args, **kwargs):  # type: (*str, **str) -> None
        super(Context, self).__init__(*args, **kwargs)
        self.id = self.context_id = self.context_id or self.id
        self.id = self.context_id = kwargs.get('context_id') or kwargs.get('id')


class Group(OxObject):
    """
    Representation of a OX group.

    When implementing a class derived from this, use BackendMetaClass as its
    metaclass.
    """
    _object_type = 'Group'

    display_name = None  # type: str
    members = []  # type: List[int]


class Resource(OxObject):
    """
    Representation of a OX Resource.

    When implementing a class derived from this, use BackendMetaClass as its
    metaclass.
    """
    _object_type = 'Resource'

    available = True
    description = None  # type: str
    display_name = None  # type: str
    email = None  # type: str

    if OX_APPSUITE_MAJOR_VERSION >= 8:
        permissions = [] # type: List[str]


class SecondaryAccount(OxObject):
    """
    Representation of a OX Secondary Account.

    When implementing a class derived from this, use BackendMetaClass as its
    metaclass.
    """
    _object_type = 'SecondaryAccount'

    email = None  # type: str
    personal = None  # type: str
    login = None  # type: str
    mail_endpoint_source = None  # type: str
    users = []  # type: List[int]
    groups = []  # type: List[int]


class UserCopy(OxObject):
    """
    Representation of a OX UserCopy module.

    When implementing a class derived from this, use BackendMetaClass as its
    metaclass.
    """
    _object_type = 'UserCopy'


class User(OxObject):
    """
    Representation of a OX User.

    When implementing a class derived from this, use BackendMetaClass as its
    metaclass.
    """
    _object_type = 'User'

    aliases = []  # type: List[str]
    anniversary = None  # type: datetime.date
    assistant_name = None  # type: str
    birthday = None  # type: datetime.date
    branches = None  # type: str
    business_category = None  # type: str
    categories = None  # type: str
    cellular_telephone1 = None  # type: str
    cellular_telephone2 = None  # type: str
    city_business = None  # type: str
    city_home = None  # type: str
    city_other = None  # type: str
    commercial_register = None  # type: str
    company = None  # type: str
    context_admin = False
    country_business = None  # type: str
    country_home = None  # type: str
    country_other = None  # type: str
    drive_user_folder_mode = None  # type: str
    default_sender_address = None   # type: str
    default_group = None  # type: Group
    department = None  # type: str
    display_name = None  # type: str
    email1 = None  # type: str
    email2 = None  # type: str
    email3 = None  # type: str
    employee_type = None  # type: str
    fax_business = None  # type: str
    fax_home = None  # type: str
    fax_other = None  # type: str
    filestore_id = None  # type: int
    filestore_name = None  # type: str
    folder_tree = None  # type: int
    given_name = None  # type: str
    gui_preferences_for_soap = None  # type: List[str]
    gui_spam_filter_enabled = None  # type: bool
    imap_login = None  # type: str
    imap_port = None  # type: int
    imap_schema = None  # type: str
    imap_server = None  # type: str
    imap_server_string = None  # type: str
    info = None  # type: str
    instant_messenger1 = None  # type: str
    instant_messenger2 = None  # type: str
    language = None  # type: str
    mail_folder_confirmed_ham_name = None  # type: str
    mail_folder_confirmed_spam_name = None  # type: str
    mail_folder_drafts_name = None  # type: str
    mail_folder_sent_name = None  # type: str
    mail_folder_spam_name = None  # type: str
    mail_folder_trash_name = None  # type: str
    mail_folder_archive_full_name = None  # type: str
    mail_enabled = True
    manager_name = None  # type: str
    marital_status = None  # type: str
    max_quota = None  # type: int
    middle_name = None  # type: str
    nickname = None  # type: str
    note = None  # type: str
    number_of_children = None  # type: str
    number_of_employee = None  # type: str
    password = None  # type: str
    password_mech = None  # type: str
    password_expired = False
    position = None  # type: str
    postal_code_business = None  # type: str
    postal_code_home = None  # type: str
    postal_code_other = None  # type: str
    primary_email = None  # type: str
    profession = None  # type: str
    room_number = None  # type: str
    sales_volume = None  # type: str
    smtp_port = None  # type: int
    smtp_schema = None  # type: str
    smtp_server = None  # type: str
    smtp_server_string = None  # type: str
    spouse_name = None  # type: str
    state_business = None  # type: str
    state_home = None  # type: str
    state_other = None  # type: str
    street_business = None  # type: str
    street_home = None  # type: str
    street_other = None  # type: str
    suffix = None  # type: str
    sur_name = None  # type: str
    tax_id = None  # type: str
    telephone_assistant = None  # type: str
    telephone_business1 = None  # type: str
    telephone_business2 = None  # type: str
    telephone_callback = None  # type: str
    telephone_car = None  # type: str
    telephone_company = None  # type: str
    telephone_home1 = None  # type: str
    telephone_home2 = None  # type: str
    telephone_ip = None  # type: str
    telephone_isdn = None  # type: str
    telephone_other = None  # type: str
    telephone_pager = None  # type: str
    telephone_primary = None  # type: str
    telephone_radio = None  # type: str
    telephone_telex = None  # type: str
    telephone_ttytdd = None  # type: str
    timezone = None  # type: str
    title = None  # type: str
    upload_file_size_limit = None  # type: int
    upload_file_size_limitPerFile = None  # type: int
    url = None  # type: str
    used_quota = None  # type: int
    user_attributes = None  # type: Dict[str, Dict[str, Union[str, Dict[str, str]]]]
    userfield01 = None  # type: str
    userfield02 = None  # type: str
    userfield03 = None  # type: str
    userfield04 = None  # type: str
    userfield05 = None  # type: str
    userfield06 = None  # type: str
    userfield07 = None  # type: str
    userfield08 = None  # type: str
    userfield09 = None  # type: str
    userfield10 = None  # type: str
    userfield11 = None  # type: str
    userfield12 = None  # type: str
    userfield13 = None  # type: str
    userfield14 = None  # type: str
    userfield15 = None  # type: str
    userfield16 = None  # type: str
    userfield17 = None  # type: str
    userfield18 = None  # type: str
    userfield19 = None  # type: str
    userfield20 = None  # type: str
    primary_account_name = None  # type: str
    convert_drive_user_folders = None
    image1 = None  # type: bytes
    image1ContentType = None  # type: str

    def get_groups(self):  # type: () -> [Group]
        """
        Retrieve groups the user is a member of.

        :return: list of Groups
        """
        raise NotImplementedError()
