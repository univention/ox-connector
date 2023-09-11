# -*- coding: utf-8 -*-
#
# OX' SOAP API object types
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

#
# Services in OX' SOAP API
# * Provision Open-Xchange using SOAP:
#   http://oxpedia.org/wiki/index.php?title=Open-Xchange_Provisioning_using_SOAP
# * API docs:
#   http://software.open-xchange.com/products/appsuite/doc/SOAP/admin/OX-Admin-SOAP.html
#
# Function descriptions can be found in the OX javadoc:
# * https://software.open-xchange.com/OX6/legacy/6.16/doc/SOAP/admin/javadoc/
# * http://software.open-xchange.com/products/appsuite/doc/RMI/javadoc/
# Method docstrings have been copied from there.
#
# Actual SOAP function signatures:
# * overview: http://<IP>/webservices/
# * WSDL: http://<IP>/webservices/OXUserService?wsdl
#

#
# The signatures of the SOAP object types can be found
# at the bottom of types.py.
# The signatures of the SOAP functions can be found
# at the bottom of this file.
#

from __future__ import absolute_import
from __future__ import annotations
import logging

try:
    from typing import Any, Optional, List, Type, TYPE_CHECKING, Union
except ImportError:
    pass

from six import with_metaclass
from zeep import Client as ZeepClient
from zeep.cache import InMemoryCache
from zeep.transports import Transport

from .config import OX_SOAP_SERVER
if TYPE_CHECKING:
    import univention.ox.soap.credentials.ClientCredentials
    import univention.ox.soap.types.Types


__all__ = ['get_ox_soap_service_class']
WS_BASE_URL = '{server}/webservices'
WS_URLS = {
    'Context': '{}/OXContextService?wsdl'.format(WS_BASE_URL),
    'Group': '{}/OXGroupService?wsdl'.format(WS_BASE_URL),
    'Resource': '{}/OXResourceService?wsdl'.format(WS_BASE_URL),
    'SecondaryAccount': '{}/OXSecondaryAccountService?wsdl'.format(
        WS_BASE_URL
    ),
    'User': '{}/OXUserService?wsdl'.format(WS_BASE_URL),
    'UserCopy': '{}/OXUserCopyService?wsdl'.format(WS_BASE_URL),
}
__ox_service_registry = dict()
logger = logging.getLogger(__name__)


def register_ox_service_class(service_type, cls):
    # type: (str, Type[OxSoapService]) -> None
    __ox_service_registry[service_type] = cls


def get_ox_soap_service_class(service_type):
    # type: (str) -> Type[OxSoapService]
    return __ox_service_registry[service_type]


def get_wsdl(server=OX_SOAP_SERVER, object_type='Context'):
    # type: (Optional[str], Optional[str]) -> zeep.wsdl.Document
    """
    Get WSDL from server.

    object_type usually doesn't matter.
    """
    return ZeepClient(WS_URLS[object_type].format(server=server)).wsdl


class OxSoapServiceError(Exception):
    pass


class OxServiceMetaClass(type):
    """
    Meta class for OX SOAP service classes. All concrete classes should
    use this as a metaclass to automatically register themselves.
    """

    def __new__(cls, clsname, bases, attrs):
        kls = super(OxServiceMetaClass, cls).__new__(
            cls, clsname, bases, attrs
        )  # type: Type[OxSoapService]
        if issubclass(kls, OxSoapService) and getattr(kls, '_type_name'):
            register_ox_service_class(kls._type_name, kls)
            logger.debug(
                'Registered class {!r} for service type {!r}.'.format(
                    cls.__name__, kls._type_name
                )
            )
        return kls


class OxSoapService(ZeepClient):
    """Base class of service classes."""

    _type_name = ''
    _ctx_arg_name = 'ctx'
    Type = None

    _transport: Transport = None

    def __init__(
        self,
        client_credentials: univention.ox.soap.credentials.ClientCredentials,
        **kwargs: str,
    ) -> None:
        assert self._type_name in WS_URLS, 'Unknown service {!r}.'.format(
            self._type_name
        )

        self.credentials = client_credentials
        self.Type = getattr(client_credentials.types, self._type_name, None)
        transport = kwargs.pop('transport', None)
        assert transport is None or isinstance(transport, Transport)
        if not transport:
            if not self._transport:
                self.__class__._transport = Transport(cache=InMemoryCache())
            transport = self._transport
        super(OxSoapService, self).__init__(
            WS_URLS[self._type_name].format(server=self.credentials.server),
            transport=transport,
            **kwargs,
        )

    def _call_ox(self, func: str, **kwargs: Any) -> Any:
        assert self.credentials.context_obj is not None
        try:
            kwargs[self._ctx_arg_name] = kwargs.pop('ctx')
        except KeyError:
            kwargs[self._ctx_arg_name] = self.credentials.context_obj
        if kwargs[self._ctx_arg_name] is None:
            del kwargs[self._ctx_arg_name]
        elif kwargs[
            self._ctx_arg_name
        ].id != self.credentials.context_obj.id and not kwargs.get('auth'):
            raise OxSoapServiceError(
                'Credentials must be supplied, when using a context different '
                'to the one used for initializing the service.'
            )
        kwargs['auth'] = (
            kwargs.pop('auth', None) or self.credentials.credentials
        )
        # Bug: OX references itself in its WSDL definition always with
        # port 80. even with https:// !
        service = self.service
        binding_options = service._binding_options
        if binding_options['address'].startswith('https://'):
            binding_options['address'] = binding_options['address'].replace(
                ':80/', ':443/'
            )
        return getattr(service, func)(**kwargs)


class OXContextService(with_metaclass(OxServiceMetaClass, OxSoapService)):
    """
    See comments in the source code of univention.ox.soap.types for dict
    representations of univention.ox.soap.types.Types.Context
    and univention.ox.soap.types.Types.UserModuleAccess.
    """

    _type_name = 'Context'

    def change(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> None:
        """
        Change specified context!

        This method currently modifies following data:
        * Login mappings - You can then login via usernam@loginmapping instead
        of username@contextID
        * Context name in configdb - This is for better organization of
        contexts in your whole system.
        * Change filestore quota size - Change how much quota the context is
        allowed to use!
        * Change storage data informations - Change filestore infos for
        context. Normally NO need to change!
        """
        return self._call_ox(
            'change', ctx=context_obj, auth=self.credentials.master_credentials
        )

    def change_capabilities(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        caps_to_add: Optional[str] = None,
        caps_to_remove: Optional[str] = None,
        caps_to_drop: Optional[str] = None,
    ) -> None:
        """
        Changes specified context's capabilities.

        :param context_obj: univention.ox.soap.types.Types.Context - Context
        :param caps_to_add: str - The capabilities to add
        :param caps_to_remove: str - The capabilities to remove
        :param caps_to_drop: str - The capabilities to drop;
            e.g. clean from storage
        :return: None
        """
        return self._call_ox(
            'changeCapabilities',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
            capsToAdd=caps_to_add,
            capsToRemove=caps_to_remove,
            capsToDrop=caps_to_drop,
        )

    def change_module_access(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        access: univention.ox.soap.types.Types.UserModuleAccess,
    ) -> None:
        """
        Change module access rights by "access combination name" for ALL users
        in the specified context.

        IF you want to change data of a context like quota etc. use Method
        change(Context ctx, Credentials auth) This method modifies ONLY the
        access rights of the context!

        :param context_obj: univention.ox.soap.types.Types.Context - A new
            Context object, this should not have been used before or a one
            returned from a previous call to this API.
        """
        return self._call_ox(
            'changeModuleAccess', ctx=context_obj, access=access
        )

    def change_module_access_by_name(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        access_combination_name: str,
    ) -> None:
        """Same as change_module_access."""
        return self._call_ox(
            'changeModuleAccessByName',
            ctx=context_obj,
            access_combination_name=access_combination_name,
        )

    def change_quota(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        module: str,
        quota_value: str,
    ) -> None:
        """
        Changes specified context's quota for a certain module.

        http://software.open-xchange.com/products/appsuite/doc/RMI/javadoc/com/openexchange/admin/rmi/OXContextInterface.html#changeQuota(
            com.openexchange.admin.rmi.dataobjects.Context, java.lang.String,
            long, com.openexchange.admin.rmi.dataobjects.Credentials)

        https://documentation.open-xchange.com/7.8.4/middleware/components/quota/quota.html

        The numeric quota value specifying the max. number of items allowed
        for context. Zero is unlimited. A value less than zero deletes the
        quota entry (and falls back to configured behavior).

        :param context_obj: univention.ox.soap.types.Types.Context - A new
            Context object, this should not have been used before or a one
            returned from a previous call to this API.
        """

        assert module in (
            'calendar',
            'task',
            'contact',
            'infostore',
            'attachment',
            'invite_guests',
            'share_links',
        )
        return self._call_ox(
            'changeQuota',
            ctx=context_obj,
            module=module,
            quotaValue=quota_value,
        )

    def create(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        admin_user: univention.ox.soap.types.Types.User,
    ) -> univention.ox.soap.types.Types.Context:
        """
        Create a new context.

        If setFilestoreId() or setWriteDatabase() has been used in the given
        context object, the context will be created in the corresponding
        database or filestore. The assigned limits to the database/filestore
        are ignored, though.

        Mandatory attributes: id, name, maxQuota

        :param context_obj: univention.ox.soap.types.Types.Context - A new
            Context object, this should not have been used before or a one
            returned from a previous call to this API.
        :param admin_user: univention.ox.soap.types.Types.User - User data of
            administrative user account for this context
        :param schema_select_strategy:
            univention.ox.soap.types.Types.SchemaSelectStrategy
        :return: None
        """
        return self._call_ox(
            'create',
            ctx=context_obj,
            admin_user=admin_user,
            auth=self.credentials.master_credentials,
        )

    def create_module_access(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        admin_user: univention.ox.soap.types.Types.User,
        access: univention.ox.soap.types.Types.UserModuleAccess,
    ) -> univention.ox.soap.types.Types.Context:
        """Same as create."""
        return self._call_ox(
            'createModuleAccess',
            ctx=context_obj,
            admin_user=admin_user,
            access=access,
            auth=self.credentials.master_credentials,
        )

    def create_module_access_by_name(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        admin_user: univention.ox.soap.types.Types.User,
        access_combination_name: str,
    ) -> univention.ox.soap.types.Types.Context:
        """Same as create."""
        return self._call_ox(
            'createModuleAccessByName',
            ctx=context_obj,
            admin_user=admin_user,
            access_combination_name=access_combination_name,
            auth=self.credentials.master_credentials,
        )

    def delete(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> None:
        """
        Delete a context.

        Note: Deleting a context will delete all data which the context
        include (all users, groups, appointments, ...)
        """
        return self._call_ox(
            'delete', ctx=context_obj, auth=self.credentials.master_credentials
        )

    def disable(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> None:
        """Disable given context."""
        return self._call_ox(
            'disable',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def disable_all(self) -> None:
        """Same as disable."""
        return self._call_ox(
            'disableAll', ctx=None, auth=self.credentials.master_credentials
        )

    def enable(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> None:
        """Enable given context."""
        return self._call_ox(
            'enable', ctx=context_obj, auth=self.credentials.master_credentials
        )

    def enable_all(self) -> None:
        """Same as enable."""
        return self._call_ox(
            'enableAll', ctx=None, auth=self.credentials.master_credentials
        )

    def exists(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> bool:
        """Determines whether a context already exists."""
        return self._call_ox(
            'exists', ctx=context_obj, auth=self.credentials.master_credentials
        )

    def downgrade(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> None:
        """
        If context was changed, call this method to flush data which is no
        longer needed due to access permission changes!
        """
        return self._call_ox(
            'downgrade',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def get_access_combination_name(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> str:
        """
        Get current access combination name of the context based on the rights
        of the admin user!

        TODO: ask OX -> this always return None for me
        """
        context_obj = self.Type(id=context_obj)
        return self._call_ox(
            'getAccessCombinationName',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def get_admin_id(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> int:
        """Determines the user ID of the admin user for a given context"""
        return self._call_ox(
            'getAdminId',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def get_context_capabilities(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> str:
        """Gets specified context's capabilities."""
        return self._call_ox(
            'getContextCapabilities',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def get_data(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> univention.ox.soap.types.Types.Context:
        """Get specified context details"""
        return self._call_ox(
            'getData',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def get_module_access(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> univention.ox.soap.types.Types.UserModuleAccess:
        """
        Get current module access rights of the context based on the rights
        of the admin user!
        """
        return self._call_ox(
            'getModuleAccess',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def list(
        self, search_pattern: str
    ) -> List[univention.ox.soap.types.Types.Context]:
        """
        Search for contexts
        Returns all contexts matching the provided search_pattern.
        """
        return self._call_ox(
            'list',
            search_pattern=search_pattern,
            ctx=None,
            auth=self.credentials.master_credentials,
        )

    def list_all(
        self,
    ) -> List[univention.ox.soap.types.Types.Context]:
        """
        Convenience method for listing all contexts Use this for search a
        context or list all contexts.
        """
        return self._call_ox(
            'listAll', ctx=None, auth=self.credentials.master_credentials
        )

    def list_by_database(
        self, db: univention.ox.soap.types.Types.Database
    ) -> List[univention.ox.soap.types.Types.Context]:
        """Search for context on specified db."""
        return self._call_ox(
            'listByDatabase', db=db, auth=self.credentials.master_credentials
        )

    def list_by_filestore(
        self, fs: univention.ox.soap.types.Types.Filestore
    ) -> List[univention.ox.soap.types.Types.Context]:
        """Search for context which store data on specified filestore"""
        return self._call_ox(
            'listByFilestore', fs=fs, auth=self.credentials.master_credentials
        )

    def list_quota(
        self, context_obj: univention.ox.soap.types.Types.Context
    ) -> List[univention.ox.soap.types.Types.Quota]:
        """Gets the configured quotas in given context."""
        return self._call_ox(
            'listQuota',
            ctx=context_obj,
            auth=self.credentials.master_credentials,
        )

    def move_context_database(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        dst_database_id: univention.ox.soap.types.Types.Database,
    ) -> int:
        """Move all data of a context contained in a database
        to another database"""
        return self._call_ox(
            'moveContextDatabase',
            ctx=context_obj,
            dst_database_id=dst_database_id,
            auth=self.credentials.master_credentials,
        )

    def move_context_filestore(
        self,
        context_obj: univention.ox.soap.types.Types.Context,
        dst_filestore_id: univention.ox.soap.types.Types.Filestore,
    ) -> int:
        """Move all data of a context contained on the filestore
        to another filestore"""
        return self._call_ox(
            'moveContextFilestore',
            ctx=context_obj,
            dst_filestore_id=dst_filestore_id,
            auth=self.credentials.master_credentials,
        )


class OXGroupService(with_metaclass(OxServiceMetaClass, OxSoapService)):
    """
    See comments in the source code of univention.ox.soap.types for dict
    representations of univention.ox.soap.types.Types.Group.
    """

    _type_name = 'Group'

    def add_member(
        self,
        grp: univention.ox.soap.types.Types.Group,
        members: List[univention.ox.soap.types.Types.User],
    ) -> None:
        """Adds a new member to the group within given context."""
        return self._call_ox('addMember', grp=grp, members=members)

    def change(self, grp: univention.ox.soap.types.Types.Group) -> None:
        """Method for changing group data in given context"""
        return self._call_ox('change', grp=grp)

    def create(self, grp: univention.ox.soap.types.Types.Group) -> None:
        """Create new group in given context."""
        return self._call_ox('create', grp=grp)

    def delete(self, grp: univention.ox.soap.types.Types.Group) -> None:
        """Delete group within given context."""
        return self._call_ox('delete', grp=grp)

    def delete_multiple(
        self, grps: List[univention.ox.soap.types.Types.Group]
    ) -> None:
        """Same as delete."""
        return self._call_ox('deleteMultiple', grps=grps)

    def get_default_group(
        self,
    ) -> univention.ox.soap.types.Types.Group:
        """Gets the default group of the specified context."""
        return self._call_ox('getDefaultGroup')

    def get_data(
        self, grp: univention.ox.soap.types.Types.Group
    ) -> univention.ox.soap.types.Types.Group:
        """Fetch a group from server."""
        return self._call_ox('getData', grp=grp)

    def get_members(
        self, grp: univention.ox.soap.types.Types.Group
    ) -> List[univention.ox.soap.types.Types.User]:
        """Get User IDs of the members of this group."""
        return self._call_ox('getMembers', grp=grp)

    def get_multiple_data(
        self, grps: List[univention.ox.soap.types.Types.Group]
    ) -> List[univention.ox.soap.types.Types.Group]:
        """Same as get_data."""
        return self._call_ox('getMultipleData', grps=grps)

    def list(self, pattern: str) -> List[univention.ox.soap.types.Types.Group]:
        """List groups within context matching the pattern."""
        return self._call_ox('list', pattern=pattern)

    def list_all(
        self,
    ) -> List[univention.ox.soap.types.Types.Group]:
        """List all groups within context."""
        return self._call_ox('listAll')

    def list_groups_for_user(
        self, user: univention.ox.soap.types.Types.User
    ) -> List[univention.ox.soap.types.Types.Group]:
        """List groups user is a member of."""
        return self._call_ox('listGroupsForUser', usr=user)

    def remove_member(
        self,
        grp: univention.ox.soap.types.Types.Group,
        members: List[univention.ox.soap.types.Types.User],
    ) -> None:
        """Remove member(s) from group."""
        return self._call_ox('removeMember', grp=grp, members=members)


class OXResourceService(with_metaclass(OxServiceMetaClass, OxSoapService)):

    _type_name = 'Resource'

    def change(self, res: univention.ox.soap.types.Types.Resource) -> None:
        return self._call_ox('change', res=res)

    def create(
        self, res: univention.ox.soap.types.Types.Resource
    ) -> univention.ox.soap.types.Types.Resource:
        return self._call_ox('create', res=res)

    def delete(self, res: univention.ox.soap.types.Types.Resource) -> None:
        return self._call_ox('delete', res=res)

    def get_data(
        self, res: univention.ox.soap.types.Types.Resource
    ) -> univention.ox.soap.types.Types.Resource:
        return self._call_ox('getData', res=res)

    def get_multiple_data(
        self, resources: List[univention.ox.soap.types.Types.Resource]
    ) -> List[univention.ox.soap.types.Types.Resource]:
        return self._call_ox('getMultipleData', resources=resources)

    def list(
        self, pattern: str
    ) -> List[univention.ox.soap.types.Types.Resource]:
        return self._call_ox('list', pattern=pattern)

    def list_all(self) -> List[univention.ox.soap.types.Types.Resource]:

        return self._call_ox('listAll')


class OXSecondaryAccountService(
    with_metaclass(OxServiceMetaClass, OxSoapService)
):

    _type_name = 'SecondaryAccount'
    _ctx_arg_name = 'context'

    def list(self):
        return self._call_ox('list')

    def create(self, account, users, groups):
        return self._call_ox(
            'create', accountDataOnCreate=account, users=users, groups=groups
        )

    def delete(self, email):
        return self._call_ox(
            'delete', primaryAddress=email, groups=[{"id": 0}]
        )


class OXUserService(with_metaclass(OxServiceMetaClass, OxSoapService)):
    """
    See comments in the source code of univention.ox.soap.types for dict
    representations of univention.ox.soap.types.Types.User.
    """

    _type_name = 'User'

    def change(self, user: univention.ox.soap.types.Types.User) -> None:
        """Manipulate user data within the given context."""
        return self._call_ox('change', usrdata=user)

    def change_by_module_access(
        self,
        user: univention.ox.soap.types.Types.User,
        module_access: univention.ox.soap.types.Types.UserModuleAccess,
    ) -> None:
        """Manipulate user module access within the given context."""
        return self._call_ox(
            'changeByModuleAccess', user=user, moduleAccess=module_access
        )

    def change_by_module_access_name(
        self,
        user: univention.ox.soap.types.Types.User,
        access_combination_name: str,
    ) -> None:
        """
        Same as change_by_module_access, but UserModuleAccess as string with
        the access combination name.
        """
        return self._call_ox(
            'changeByModuleAccessName',
            user=user,
            access_combination_name=access_combination_name,
        )

    def change_capabilities(
        self,
        user: univention.ox.soap.types.Types.User,
        caps_to_add: str = '',
        caps_to_remove: str = '',
        caps_to_drop: str = '',
    ) -> None:
        """Changes specified user's capabilities."""
        return self._call_ox(
            'changeCapabilities',
            user=user,
            capsToAdd=caps_to_add,
            capsToRemove=caps_to_remove,
            capsToDrop=caps_to_drop,
        )

    def change_mail_address_personal(
        self, user: univention.ox.soap.types.Types.User, local_part: str
    ) -> None:
        """Changes the personal part of specified user's E-Mail address."""
        return self._call_ox(
            'changeMailAddressPersonal', user=user, personal=local_part
        )

    def change_module_access_global(
        self,
        filter_s: str = '',
        add_access: univention.ox.soap.types.Types.UserModuleAccess = None,
        remove_access: univention.ox.soap.types.Types.UserModuleAccess = None,
    ) -> None:
        """
        This method changes module Permissions for all (!) users in all (!)
        contexts. This can be filtered by already existing access combinations.
        If no filter is given, all users are changed.

        :param filter_s: str - The call affects only users with exactly this
            access combination. This is either a String representing a defined
            module access combination or an Integer (masked as String) for
            direct definitions. null for no filter.
        :param add_access: UserModuleAccess - Access rights to be added
        :param remove_access: UserModuleAccess - Access rights to be removed
        :return: None
        """
        return self._call_ox(
            'changeModuleAccessGlobal',
            auth=self.credentials.master_credentials,
            filter=filter_s,
            addAccess=add_access,
            removeAccess=remove_access,
        )

    def create(
        self, user: univention.ox.soap.types.Types.User
    ) -> univention.ox.soap.types.Types.User:
        """
        Creates a new user within the given context.
        Default context access rights are used!
        Mandatory attributes: name, display_name, password, given_name,
                              sur_name, primaryEmail, email1
        """
        return self._call_ox('create', usrdata=user)

    def create_by_module_access(
        self,
        user: univention.ox.soap.types.Types.User,
        module_access: univention.ox.soap.types.Types.UserModuleAccess,
    ) -> univention.ox.soap.types.Types.User:
        """Same as create."""
        return self._call_ox(
            'createByModuleAccess', usrdata=user, access=module_access
        )

    def create_by_module_access_name(
        self,
        user: univention.ox.soap.types.Types.User,
        access_combination_name: str,
    ) -> None:
        """Same as create."""
        return self._call_ox(
            'createByModuleAccessName',
            usrdata=user,
            access_combination_name=access_combination_name,
        )

    def delete(
        self,
        user: univention.ox.soap.types.Types.User,
        reassign: Optional[int] = None,
    ) -> None:
        """
        Delete user from given context.

        Regarding `reassign': see
        https://oxpedia.org/wiki/index.php?title=AppSuite:File_Storages_per_User

        If `reassign' is None, data will not be reassigned.
        """
        kwargs = dict(user=user)
        if reassign is not None:
            kwargs['reassign'] = int(reassign)
        return self._call_ox('delete', **kwargs)

    def delete_multiple(
        self, users: List[univention.ox.soap.types.Types.User], reassign: int
    ) -> None:
        """Same as delete."""
        kwargs = dict(users=users)
        if reassign is not None:
            kwargs['reassign'] = int(reassign)
        return self._call_ox('deleteMultiple', **kwargs)

    def exists(self, user: univention.ox.soap.types.Types.User) -> None:
        """
        Check whether the given user exists.
        """
        return self._call_ox('exists', user=user)

    def get_access_combination_name(
        self, user: univention.ox.soap.types.Types.User
    ) -> Union[str, None]:
        """
        Get current access combination name of an user!
        Check return value (can be None).

        :returns str|None - Access combination name or null if current access
            rights cannot be mapped to an access combination name.
        """
        return self._call_ox('getAccessCombinationName', user=user)

    def get_context_admin(self) -> univention.ox.soap.types.Types.User:
        """Returns the Context admin User object"""
        return self._call_ox('getContextAdmin')

    def get_data(self, user: univention.ox.soap.types.Types.User) -> None:
        """Retrieve user objects (requires username or id)."""
        return self._call_ox('getData', user=user)

    def get_module_access(
        self, user: univention.ox.soap.types.Types.User
    ) -> univention.ox.soap.types.Types.UserModuleAccess:
        """Retrieve the ModuleAccess for an user."""
        return self._call_ox('getModuleAccess', user=user)

    def get_multiple_data(
        self, users: List[univention.ox.soap.types.Types.User]
    ) -> List[univention.ox.soap.types.Types.User]:
        """Same as get_data."""
        return self._call_ox('getMultipleData', users=users)

    def get_user_capabilities(
        self, user: univention.ox.soap.types.Types.User
    ) -> str:
        """Gets specified user's capabilities."""
        return self._call_ox('getUserCapabilities', user=user)

    def list(
        self,
        search_pattern: str,
        include_guests: bool = True,
        exclude_users: bool = False,
    ) -> List[univention.ox.soap.types.Types.User]:
        r"""
        Retrieve all users for a given context.

        The search pattern is directly transformed into a SQL LIKE string
        comparison, where a * is transformed into a % a % and a _ must be
        escaped by a \ (e.g. if you want to search for _doe, use the
        pattern \_doe

        :param search_pattern: str - search pattern
        :param include_guests: bool - List guest users too
        :param exclude_users: bool - List only guest users
        :return: User[] with currently ONLY id set in each User.
        """
        return self._call_ox(
            'list',
            search_pattern=search_pattern,
            include_guests=include_guests,
            exclude_users=exclude_users,
        )

    def list_all(
        self, include_guests: bool = True, exclude_users: bool = False
    ) -> List[univention.ox.soap.types.Types.User]:
        """
        Retrieve all users for a given context.

        The same as calling list with a search_pattern of "*"
        """
        return self._call_ox(
            'listAll',
            include_guests=include_guests,
            exclude_users=exclude_users,
        )

    def list_by_alias_domain(
        self, alias_domain: str
    ) -> List[univention.ox.soap.types.Types.User]:
        """
        Retrieve users with the supplied domain used in its `aliases` field.
        :param alias_domain: str: domain name
        :return: list of User objects
        """
        return self._call_ox('listByAliasDomain', alias_domain=alias_domain)

    def list_case_insensitive(
        self, search_pattern: str
    ) -> List[univention.ox.soap.types.Types.User]:
        """Same as list."""
        return self._call_ox(
            'listCaseInsensitive', search_pattern=search_pattern
        )

    def move_from_context_to_user_filestore(
        self,
        user: univention.ox.soap.types.Types.User,
        dst_filestore: univention.ox.soap.types.Types.Filestore,
        max_quota: float,
    ) -> int:

        """
        Moves a user's files from a context to his own storage.

        This operation is quota-aware and thus transfers current quota usage
        from context to user.

        :return: int - The job identifier which can be used for retrieving
            progress information.
        """
        return self._call_ox(
            'moveFromContextToUserFilestore',
            user=user,
            dst_filestore_id=dst_filestore,
            max_quota=max_quota,
        )

    def move_from_master_to_user_filestore(
        self,
        user: univention.ox.soap.types.Types.User,
        master_user: univention.ox.soap.types.Types.User,
        dst_filestore: univention.ox.soap.types.Types.Filestore,
        max_quota: float,
    ) -> int:

        """
        Moves a user's files from a master account to his own storage.

        This operation is quota-aware and thus transfers current quota usage
        from master account to user.

        :return: int - The job identifier which can be used for retrieving
            progress information.
        """
        return self._call_ox(
            'moveFromMasterToUserFilestore',
            user=user,
            masterUser=master_user,
            dst_filestore_id=dst_filestore,
            max_quota=max_quota,
        )

    def move_from_user_filestore_to_master(
        self,
        user: univention.ox.soap.types.Types.User,
        master_user: univention.ox.soap.types.Types.User,
    ) -> int:

        """
        Moves a user's files from his own storage to the storage of specified
        master.

        This operation is quota-aware and thus transfers current quota usage
        to master account as well.

        :return: int - The job identifier which can be used for retrieving
            progress information.
        """
        return self._call_ox(
            'moveFromUserFilestoreToMaster', user=user, masterUser=master_user
        )

    def move_from_user_to_context_filestore(
        self, user: univention.ox.soap.types.Types.User
    ) -> int:
        """
        Moves a user's files from his own to a context storage.
        This operation is quota-aware and thus transfers current quota usage
        from user to context.

        :return: int - The job identifier which can be used for retrieving
            progress information.
        """
        return self._call_ox('moveFromUserToContextFilestore', user=user)

    def move_user_filestore(
        self,
        user: univention.ox.soap.types.Types.User,
        dst_filestore: univention.ox.soap.types.Types.Filestore,
    ) -> int:

        """
        Moves a user's files from one storage to another.

        This operation leaves quota usage unchanged and thus can be considered
        as the user-sensitive counterpart for
        OXContextInterface.moveContextFilestore().

        :return: int - The job identifier which can be used for retrieving
            progress information.
        """
        return self._call_ox(
            'moveUserFilestore', user=user, dst_filestore_id=dst_filestore
        )


class OXUserCopyService(with_metaclass(OxServiceMetaClass, OxSoapService)):

    _type_name = 'UserCopy'
    _ctx_arg_name = 'src'

    def copy_user(
        self,
        user: univention.ox.soap.types.Types.User,
        dest_ctx: univention.ox.soap.types.Types.Context,
    ) -> univention.ox.soap.types.Types.User:
        return self._call_ox(
            'copyUser',
            user=user,
            dest=dest_ctx,
            auth=self.credentials.master_credentials,
        )


######################################
# Below are SOAP function signatures #
######################################

#
# The signatures of the SOAP object types can be found at
# the bottom of types.py.
#

# Service: OXContextService
#
# change(ctx: ns4:Context, auth: ns5:Credentials) -> None
# changeCapabilities(ctx: ns4:Context, capsToAdd: xsd:string,
#     capsToRemove: xsd:string, capsToDrop: xsd:string, auth: ns5:Credentials)
#     -> None
# changeModuleAccess(ctx: ns4:Context, access: ns4:UserModuleAccess,
#     auth: ns5:Credentials) -> None
# changeModuleAccessByName(ctx: ns4:Context,
#     access_combination_name: xsd:string, auth: ns5:Credentials) -> None
# changeQuota(ctx: ns4:Context, module: xsd:string, quotaValue: xsd:string,
#     auth: ns5:Credentials) -> None
# checkCountsConsistency(checkDatabaseCounts: xsd:boolean,
#     checkFilestoreCounts: xsd:boolean, auth: ns5:Credentials) -> None
# create(ctx: ns4:Context, admin_user: ns4:User, auth: ns5:Credentials,
#     schema_select_strategy: ns4:SchemaSelectStrategy) -> return: ns4:Context
# createModuleAccess(ctx: ns4:Context, admin_user: ns4:User,
#     access: ns4:UserModuleAccess, auth: ns5:Credentials,
#     schema_select_strategy: ns4:SchemaSelectStrategy) -> return: ns4:Context
# createModuleAccessByName(ctx: ns4:Context, admin_accessuser: ns4:User,
#     access_combination_name: xsd:string, auth: ns5:Credentials,
#     schema_select_strategy: ns4:SchemaSelectStrategy) -> return: ns4:Context
# delete(ctx: ns4:Context, auth: ns5:Credentials) -> None
# disable(ctx: ns4:Context, auth: ns5:Credentials) -> None
# disableAll(auth: ns5:Credentials) -> None
# downgrade(ctx: ns4:Context, auth: ns5:Credentials) -> None
# enable(ctx: ns4:Context, auth: ns5:Credentials) -> None
# enableAll(auth: ns5:Credentials) -> None
# exists(ctx: ns4:Context, auth: ns5:Credentials) -> return: xsd:boolean
# getAccessCombinationName(ctx: ns4:Context, auth: ns5:Credentials)
#     -> return: xsd:string
# getAdminId(ctx: ns4:Context, auth: ns5:Credentials) -> return: xsd:int
# getContextCapabilities(ctx: ns4:Context, auth: ns5:Credentials)
#     -> return: xsd:string
# getData(ctx: ns4:Context, auth: ns5:Credentials) -> return: ns4:Context
# getModuleAccess(ctx: ns4:Context, auth: ns5:Credentials)
#     -> return: ns4:UserModuleAccess
# list(search_pattern: xsd:string, auth: ns5:Credentials)
#     -> return: ns4:Context[]
# listAll(auth: ns5:Credentials) -> return: ns4:Context[]
# listByDatabase(db: ns4:Database, auth: ns5:Credentials)
#     -> return: ns4:Context[]
# listByFilestore(fs: ns4:Filestore, auth: ns5:Credentials)
#     -> return: ns4:Context[]
# listPage(search_pattern: xsd:string, offset: xsd:string, length: xsd:string,
#     auth: ns5:Credentials) -> return: ns4:Context[]
# listPageAll(offset: xsd:string, length: xsd:string, auth: ns5:Credentials)
#     -> return: ns4:Context[]
# listPageByDatabase(db: ns4:Database, offset: xsd:string, length: xsd:string,
#     auth: ns5:Credentials) -> return: ns4:Context[]
# listPageByFilestore(fs: ns4:Filestore, offset: xsd:string,
#     length: xsd:string, auth: ns5:Credentials) -> return: ns4:Context[]
# listQuota(ctx: ns4:Context, auth: ns5:Credentials) -> return: ns5:Quota[]
# moveContextDatabase(ctx: ns4:Context, dst_database_id: ns4:Database,
#     auth: ns5:Credentials) -> return: xsd:int
# moveContextFilestore(ctx: ns4:Context, dst_filestore_id: ns4:Filestore,
#     auth: ns5:Credentials) -> return: xsd:int

# Service: OXGroupService
#
# addMember(ctx: ns4:Context, grp: ns4:Group, members: ns4:User[],
#     auth: ns5:Credentials) -> None
# change(ctx: ns4:Context, grp: ns4:Group, auth: ns5:Credentials) -> None
# create(ctx: ns4:Context, grp: ns4:Group, auth: ns5:Credentials)
#     -> return: ns4:Group
# delete(ctx: ns4:Context, grp: ns4:Group, auth: ns5:Credentials) -> None
# deleteMultiple(ctx: ns4:Context, grps: ns4:Group[], auth: ns5:Credentials)
#     -> None
# getData(ctx: ns4:Context, grp: ns4:Group, auth: ns5:Credentials)
#     -> return: ns4:Group
# getDefaultGroup(ctx: ns4:Context, auth: ns5:Credentials) -> return: ns4:Group
# getMembers(ctx: ns4:Context, grp: ns4:Group, auth: ns5:Credentials)
#     -> return: ns4:User[]
# getMultipleData(ctx: ns4:Context, grps: ns4:Group[], auth: ns5:Credentials)
#     -> return: ns4:Group[]
# list(ctx: ns4:Context, pattern: xsd:string, auth: ns5:Credentials)
#     -> return: ns4:Group[]
# listAll(ctx: ns4:Context, auth: ns5:Credentials) -> return: ns4:Group[]
# listGroupsForUser(ctx: ns4:Context, usr: ns4:User, auth: ns5:Credentials)
#     -> return: ns4:Group[]
# removeMember(ctx: ns4:Context, grp: ns4:Group, members: ns4:User[],
#     auth: ns5:Credentials) -> None

# Service: OXUserService
#
# change(ctx: ns4:Context, usrdata: ns4:User, auth: ns5:Credentials) -> None
# changeByModuleAccess(ctx: ns4:Context, user: ns4:User,
#     moduleAccess: ns4:UserModuleAccess, auth: ns5:Credentials) -> None
# changeByModuleAccessName(ctx: ns4:Context, user: ns4:User,
#     access_combination_name: xsd:string, auth: ns5:Credentials) -> None
# changeCapabilities(ctx: ns4:Context, user: ns4:User, capsToAdd: xsd:string,
#     capsToRemove: xsd:string, capsToDrop: xsd:string, auth: ns5:Credentials)
#     -> None
# changeMailAddressPersonal(ctx: ns4:Context, user: ns4:User,
#     personal: xsd:string, auth: ns5:Credentials) -> None
# changeModuleAccessGlobal(filter: xsd:string, addAccess: ns4:UserModuleAccess,
#     removeAccess: ns4:UserModuleAccess, auth: ns5:Credentials) -> None
# create(ctx: ns4:Context, usrdata: ns4:User, auth: ns5:Credentials)
#     -> return: ns4:User
# createByModuleAccess(ctx: ns4:Context, usrdata: ns4:User,
#     access: ns4:UserModuleAccess, auth: ns5:Credentials) -> return: ns4:User
# createByModuleAccessName(ctx: ns4:Context, usrdata: ns4:User,
#     access_combination_name: xsd:string, auth: ns5:Credentials)
#     -> return: ns4:User
# delete(ctx: ns4:Context, user: ns4:User, auth: ns5:Credentials,
#     reassign: xsd:int) -> None
# deleteMultiple(ctx: ns4:Context, users: ns4:User[], auth: ns5:Credentials,
#     reassign: xsd:int) -> None
# exists(ctx: ns4:Context, user: ns4:User, auth: ns5:Credentials)
#     -> return: xsd:boolean
# getAccessCombinationName(ctx: ns4:Context, user: ns4:User,
#     auth: ns5:Credentials) -> return: xsd:string
# getContextAdmin(ctx: ns4:Context, auth: ns5:Credentials) -> return: ns4:User
# getData(ctx: ns4:Context, user: ns4:User, auth: ns5:Credentials)
#     -> return: ns4:User
# getModuleAccess(ctx: ns4:Context, user: ns4:User, auth: ns5:Credentials)
#     -> return: ns4:UserModuleAccess
# getMultipleData(ctx: ns4:Context, users: ns4:User[], auth: ns5:Credentials)
#     -> return: ns4:User[]
# getUserCapabilities(ctx: ns4:Context, user: ns4:User, auth: ns5:Credentials)
#     -> return: xsd:string
# list(ctx: ns4:Context, search_pattern: xsd:string, auth: ns5:Credentials,
#     include_guests: xsd:boolean, exclude_users: xsd:boolean)
#     -> return: ns4:User[]
# listAll(ctx: ns4:Context, auth: ns5:Credentials, include_guests: xsd:boolean,
#     exclude_users: xsd:boolean) -> return: ns4:User[]
# listByAliasDomain(ctx: ns4:Context, alias_domain: xsd:string,
#     auth: ns5:Credentials) -> return: ns4:User[]
# listCaseInsensitive(ctx: ns4:Context, search_pattern: xsd:string,
#     auth: ns5:Credentials) -> return: ns4:User[]
# moveFromContextToUserFilestore(ctx: ns4:Context, user: ns4:User,
#     dst_filestore_id: ns4:Filestore, max_quota: xsd:long,
#     auth: ns5:Credentials) -> return: xsd:int
# moveFromMasterToUserFilestore(ctx: ns4:Context, user: ns4:User,
#     masterUser: ns4:User, dst_filestore_id: ns4:Filestore,
#     max_quota: xsd:long, auth: ns5:Credentials) -> return: xsd:int
# moveFromUserFilestoreToMaster(ctx: ns4:Context, user: ns4:User,
#     masterUser: ns4:User, auth: ns5:Credentials) -> return: xsd:int
# moveFromUserToContextFilestore(ctx: ns4:Context, user: ns4:User,
#     auth: ns5:Credentials) -> return: xsd:int
# moveUserFilestore(ctx: ns4:Context, user: ns4:User,
#     dst_filestore_id: ns4:Filestore, auth: ns5:Credentials)
#     -> return: xsd:int

# Service: OXResourceService
#
# change(ctx: ns4:Context, res: ns4:Resource, auth: ns5:Credentials) -> None
# create(ctx: ns4:Context, res: ns4:Resource, auth: ns5:Credentials)
#     -> return: ns4:Resource
# delete(ctx: ns4:Context, res: ns4:Resource, auth: ns5:Credentials) -> None
# getData(ctx: ns4:Context, res: ns4:Resource, auth: ns5:Credentials)
#     -> return: ns4:Resource
# getMultipleData(ctx: ns4:Context, resources: ns4:Resource[],
#     auth: ns5:Credentials) -> return: ns4:Resource[]
# list(ctx: ns4:Context, pattern: xsd:string, auth: ns5:Credentials)
#     -> return: ns4:Resource[]
# listAll(ctx: ns4:Context, auth: ns5:Credentials) -> return: ns4:Resource[]

# Service: OXUserCopy
#
# copyUser(user: ns1:User, src: ns1:Context, dest: ns1:Context,
#     auth: ns2:Credentials) -> ns1:User
