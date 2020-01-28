# -*- coding: utf-8 -*-
#
# OX' SOAP API object types
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

#
# Object types in OX' SOAP API
# Provision Open-Xchange using SOAP: http://oxpedia.org/wiki/index.php?title=Open-Xchange_Provisioning_using_SOAP
# API docs: http://software.open-xchange.com/products/appsuite/doc/SOAP/admin/OX-Admin-SOAP.html
# WSDL: http://<IP>/webservices/OXContextService?wsdl
#

#
# The signatures of the SOAP object types can be found at the bottom of this file
# The signatures of the SOAP functions can be found at the bottom of services.py.
#

#
# zeep.objects.X is the same as univention.ox.soap.types.Types.X
#

from __future__ import absolute_import

from .services import get_wsdl
from .soap_config import SERVER


# The SOAP object classes have to be fetched once through the network.
# Doing that in __init__ to prevent network activity at import time.


class Types(object):
	"""
	See comments in the source code of this class for dict-representations of
	the SOAP classes.
	"""
	wsdl_context = None
	wsdl_group = None
	wsdl_resource = None
	wsdl_user = None

	def __init__(self, server=SERVER):  # type: (Optional[str]) -> None
		if not self.wsdl_context:
			self.__class__.wsdl_context = get_wsdl(server, 'Context')
		if not self.wsdl_group:
			self.__class__.wsdl_group = get_wsdl(server, 'Group')
		if not self.wsdl_resource:
			self.__class__.wsdl_resource = get_wsdl(server, 'Resource')
		if not self.wsdl_user:
			self.__class__.wsdl_user = get_wsdl(server, 'User')
		self.Credentials = self.wsdl_context.types.get_type('{http://dataobjects.rmi.admin.openexchange.com/xsd}Credentials')
		self.Context = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}Context')
		self.Database = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}Database')
		self.Entry = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}Entry')
		self.Filestore = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}Filestore')
		self.Group = self.wsdl_group.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}Group')
		self.Quota = self.wsdl_context.types.get_type('{http://dataobjects.rmi.admin.openexchange.com/xsd}Quota')
		self.Resource = self.wsdl_resource.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}Resource')
		self.SchemaSelectStrategy = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}SchemaSelectStrategy')
		self.SOAPMapEntry = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}SOAPMapEntry')
		self.SOAPStringMap = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}SOAPStringMap')
		self.SOAPStringMapMap = self.wsdl_context.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}SOAPStringMapMap')
		self.User = self.wsdl_user.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}User')
		self.UserModuleAccess = self.wsdl_user.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}UserModuleAccess')


####################################
# Below are SOAP object signatures #
####################################

# Prefixes:
#      xsd: http://www.w3.org/2001/XMLSchema
#      ns0: http://soap.admin.openexchange.com
#      ns1: http://rmi.java/xsd
#      ns2: http://io.java/xsd
#      ns3: http://exceptions.rmi.admin.openexchange.com/xsd
#      ns4: http://dataobjects.soap.admin.openexchange.com/xsd
#      ns5: http://dataobjects.rmi.admin.openexchange.com/xsd
#

# Global elements:
#      ns0:ContextExistsException(ContextExistsException: ns3:ContextExistsException)
#      ns0:DatabaseUpdateException(DatabaseUpdateException: ns3:DatabaseUpdateException)
#      ns0:InvalidCredentialsException(InvalidCredentialsException: ns3:InvalidCredentialsException)
#      ns0:InvalidDataException(InvalidDataException: ns3:InvalidDataException)
#      ns0:NoSuchContextException(NoSuchContextException: ns3:NoSuchContextException)
#      ns0:NoSuchDatabaseException(NoSuchDatabaseException: ns3:NoSuchDatabaseException)
#      ns0:NoSuchFilestoreException(NoSuchFilestoreException: ns3:NoSuchFilestoreException)
#      ns0:NoSuchReasonException(NoSuchReasonException: ns3:NoSuchReasonException)
#      ns0:OXContextException(OXContextException: ns3:OXContextException)
#      ns0:RemoteException(RemoteException: ns1:RemoteException)
#      ns0:StorageException(StorageException: ns3:StorageException)
#      ns0:change(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:changeCapabilities(ctx: ns4:Context, capsToAdd: xsd:string, capsToRemove: xsd:string, capsToDrop: xsd:string, auth: ns5:Credentials)
#      ns0:changeModuleAccess(ctx: ns4:Context, access: ns4:UserModuleAccess, auth: ns5:Credentials)
#      ns0:changeModuleAccessByName(ctx: ns4:Context, access_combination_name: xsd:string, auth: ns5:Credentials)
#      ns0:changeQuota(ctx: ns4:Context, module: xsd:string, quotaValue: xsd:string, auth: ns5:Credentials)
#      ns0:checkCountsConsistency(checkDatabaseCounts: xsd:boolean, checkFilestoreCounts: xsd:boolean, auth: ns5:Credentials)
#      ns0:create(ctx: ns4:Context, admin_user: ns4:User, auth: ns5:Credentials, schema_select_strategy: ns4:SchemaSelectStrategy)
#      ns0:createModuleAccess(ctx: ns4:Context, admin_user: ns4:User, access: ns4:UserModuleAccess, auth: ns5:Credentials, schema_select_strategy: ns4:SchemaSelectStrategy)
#      ns0:createModuleAccessByName(ctx: ns4:Context, admin_user: ns4:User, access_combination_name: xsd:string, auth: ns5:Credentials, schema_select_strategy: ns4:SchemaSelectStrategy)
#      ns0:createModuleAccessByNameResponse(return: ns4:Context)
#      ns0:createModuleAccessResponse(return: ns4:Context)
#      ns0:createResponse(return: ns4:Context)
#      ns0:delete(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:disable(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:disableAll(auth: ns5:Credentials)
#      ns0:downgrade(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:enable(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:enableAll(auth: ns5:Credentials)
#      ns0:exists(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:existsResponse(return: xsd:boolean)
#      ns0:getAccessCombinationName(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:getAccessCombinationNameResponse(return: xsd:string)
#      ns0:getAdminId(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:getAdminIdResponse(return: xsd:int)
#      ns0:getContextCapabilities(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:getContextCapabilitiesResponse(return: xsd:string)
#      ns0:getData(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:getDataResponse(return: ns4:Context)
#      ns0:getModuleAccess(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:getModuleAccessResponse(return: ns4:UserModuleAccess)
#      ns0:list(search_pattern: xsd:string, auth: ns5:Credentials)
#      ns0:listAll(auth: ns5:Credentials)
#      ns0:listAllResponse(return: ns4:Context[])
#      ns0:listByDatabase(db: ns4:Database, auth: ns5:Credentials)
#      ns0:listByDatabaseResponse(return: ns4:Context[])
#      ns0:listByFilestore(fs: ns4:Filestore, auth: ns5:Credentials)
#      ns0:listByFilestoreResponse(return: ns4:Context[])
#      ns0:listPage(search_pattern: xsd:string, offset: xsd:string, length: xsd:string, auth: ns5:Credentials)
#      ns0:listPageAll(offset: xsd:string, length: xsd:string, auth: ns5:Credentials)
#      ns0:listPageAllResponse(return: ns4:Context[])
#      ns0:listPageByDatabase(db: ns4:Database, offset: xsd:string, length: xsd:string, auth: ns5:Credentials)
#      ns0:listPageByDatabaseResponse(return: ns4:Context[])
#      ns0:listPageByFilestore(fs: ns4:Filestore, offset: xsd:staccessring, length: xsd:string, auth: ns5:Credentials)
#      ns0:listPageByFilestoreResponse(return: ns4:Context[])
#      ns0:listPageResponse(return: ns4:Context[])
#      ns0:listQuota(ctx: ns4:Context, auth: ns5:Credentials)
#      ns0:listQuotaResponse(return: ns5:Quota[])
#      ns0:listResponse(return: ns4:Context[])
#      ns0:moveContextDatabase(ctx: ns4:Context, dst_database_id: ns4:Database, auth: ns5:Credentials)
#      ns0:moveContextDatabaseResponse(return: xsd:int)
#      ns0:moveContextFilestore(ctx: ns4:Context, dst_filestore_id: ns4:Filestore, auth: ns5:Credentials)
#      ns0:moveContextFilestoreResponse(return: xsd:int)
#

# Global types:
#      xsd:anyType
#      ns5:Credentials(login: xsd:string, password: xsd:string)
#      ns5:Quota(module: xsd:string, limit: xsd:long)
#      ns4:Context(average_size: xsd:long, enabled: xsd:boolean, filestoreId: xsd:int, filestore_name: xsd:string, id: xsd:int, loginMappings: xsd:string[], maxQuota: xsd:long, name: xsd:string, readDatabase: ns4:Database, usedQuota: xsd:long, userAttributes: ns4:SOAPStringMapMap, writeDatabase: ns4:Database)
#      ns4:Database(currentUnits: xsd:int, driver: xsd:string, id: xsd:int, login: xsd:string, master: xsd:boolean, masterId: xsd:int, maxUnits: xsd:int, name: xsd:string, password: xsd:string, poolHardLimit: xsd:int, poolInitial: xsd:int, poolMax: xsd:int, read_id: xsd:int, scheme: xsd:string, url: xsd:string)
#      ns4:Entry(key: xsd:string, value: xsd:string)
#      ns4:Filestore(currentContexts: xsd:int, id: xsd:int, maxContexts: xsd:int, reserved: xsd:long, size: xsd:long, url: xsd:string, used: xsd:long)
#      ns4:Resource(available: xsd:boolean, description: xsd:string, displayname: xsd:string, email: xsd:string, id: xsd:int, name: xsd:string)
#      ns4:Group(displayname: xsd:string, id: xsd:int, members: xsd:int[], name: xsd:string)
#      ns4:SOAPMapEntry(key: xsd:string, value: ns4:SOAPStringMap)
#      ns4:SOAPStringMap(entries: ns4:Entry[])
#      ns4:SOAPStringMapMap(entries: ns4:SOAPMapEntry[])
#      ns4:SchemaSelectStrategy(schema_name: xsd:string, strategy: xsd:string)
#      ns4:User(aliases: xsd:string[], anniversary: xsd:date, assistant_name: xsd:string, birthday: xsd:date, branches: xsd:string, business_category: xsd:string, categories: xsd:string, cellular_telephone1: xsd:string, cellular_telephone2: xsd:string, city_business: xsd:string, city_home: xsd:string, city_other: xsd:string, commercial_register: xsd:string, company: xsd:string, contextadmin: xsd:boolean, country_business: xsd:string, country_home: xsd:string, country_other: xsd:string, drive_user_folder_mode: xsd:string, defaultSenderAddress: xsd:string, default_group: {http://dataobjects.soap.admin.openexchange.com/xsd}Group, department: xsd:string, display_name: xsd:string, email1: xsd:string, email2: xsd:string, email3: xsd:string, employeeType: xsd:string, fax_business: xsd:string, fax_home: xsd:string, fax_other: xsd:string, filestoreId: xsd:int, filestore_name: xsd:string, folderTree: xsd:int, given_name: xsd:string, guiPreferencesForSoap: {http://dataobjects.soap.admin.openexchange.com/xsd}SOAPStringMap, gui_spam_filter_enabled: xsd:boolean, id: xsd:int, imapLogin: xsd:string, imapPort: xsd:int, imapSchema: xsd:string, imapServer: xsd:string, imapServerString: xsd:string, info: xsd:string, instant_messenger1: xsd:string, instant_messenger2: xsd:string, language: xsd:string, mail_folder_confirmed_ham_name: xsd:string, mail_folder_confirmed_spam_name: xsd:string, mail_folder_drafts_name: xsd:string, mail_folder_sent_name: xsd:string, mail_folder_spam_name: xsd:string, mail_folder_trash_name: xsd:string, mail_folder_archive_full_name: xsd:string, mailenabled: xsd:boolean, manager_name: xsd:string, marital_status: xsd:string, maxQuota: xsd:long, middle_name: xsd:string, name: xsd:string, nickname: xsd:string, note: xsd:string, number_of_children: xsd:string, number_of_employee: xsd:string, password: xsd:string, passwordMech: xsd:string, password_expired: xsd:boolean, position: xsd:string, postal_code_business: xsd:string, postal_code_home: xsd:string, postal_code_other: xsd:string, primaryEmail: xsd:string, profession: xsd:string, room_number: xsd:string, sales_volume: xsd:string, smtpPort: xsd:int, smtpSchema: xsd:string, smtpServer: xsd:string, smtpServerString: xsd:string, spouse_name: xsd:string, state_business: xsd:string, state_home: xsd:string, state_other: xsd:string, street_business: xsd:string, street_home: xsd:string, street_other: xsd:string, suffix: xsd:string, sur_name: xsd:string, tax_id: xsd:string, telephone_assistant: xsd:string, telephone_business1: xsd:string, telephone_business2: xsd:string, telephone_callback: xsd:string, telephone_car: xsd:string, telephone_company: xsd:string, telephone_home1: xsd:string, telephone_home2: xsd:string, telephone_ip: xsd:string, telephone_isdn: xsd:string, telephone_other: xsd:string, telephone_pager: xsd:string, telephone_primary: xsd:string, telephone_radio: xsd:string, telephone_telex: xsd:string, telephone_ttytdd: xsd:string, timezone: xsd:string, title: xsd:string, uploadFileSizeLimit: xsd:int, uploadFileSizeLimitPerFile: xsd:int, url: xsd:string, usedQuota: xsd:long, userAttributes: {http://dataobjects.soap.admin.openexchange.com/xsd}SOAPStringMapMap, userfield01: xsd:string, userfield02: xsd:string, userfield03: xsd:string, userfield04: xsd:string, userfield05: xsd:string, userfield06: xsd:string, userfield07: xsd:string, userfield08: xsd:string, userfield09: xsd:string, userfield10: xsd:string, userfield11: xsd:string, userfield12: xsd:string, userfield13: xsd:string, userfield14: xsd:string, userfield15: xsd:string, userfield16: xsd:string, userfield17: xsd:string, userfield18: xsd:string, userfield19: xsd:string, userfield20: xsd:string, primaryAccountName: xsd:string, convert_drive_user_folders: xsd:boolean)'

#      ns4:UserModuleAccess(OLOX20: xsd:boolean, USM: xsd:boolean, activeSync: xsd:boolean, calendar: xsd:boolean, collectEmailAddresses: xsd:boolean, contacts: xsd:boolean, delegateTask: xsd:boolean, deniedPortal: xsd:boolean, editGroup: xsd:boolean, editPassword: xsd:boolean, editPublicFolders: xsd:boolean, editResource: xsd:boolean, globalAddressBookDisabled: xsd:boolean, ical: xsd:boolean, infostore: xsd:boolean, multipleMailAccounts: xsd:boolean, publicFolderEditable: xsd:boolean, publication: xsd:boolean, readCreateSharedFolders: xsd:boolean, subscription: xsd:boolean, syncml: xsd:boolean, tasks: xsd:boolean, vcard: xsd:boolean, webdav: xsd:boolean, webdavXml: xsd:boolean, webmail: xsd:boolean)
#      ns3:ContextExistsException(Exception: None)
#      ns3:DatabaseUpdateException(Exception: None)
#      ns3:InvalidCredentialsException(Exception: None)
#      ns3:InvalidDataException(Exception: None, objectname: xsd:string)
#      ns3:NoSuchContextException(Exception: None)
#      ns3:NoSuchDatabaseException(Exception: None)
#      ns3:NoSuchFilestoreException(Exception: None)
#      ns3:NoSuchReasonException(Exception: None)
#      ns3:OXContextException(Exception: None)
#      ns3:StorageException(Exception: None)
#      ns2:IOException(Exception: None)
#      ns1:RemoteException(Exception: None, message: xsd:string)
#      ns0:Exception(Exception: None)
#      xsd:ENTITIES
#      xsd:ENTITY
#      xsd:ID
#      xsd:IDREF
#      xsd:IDREFS
#      xsd:NCName
#      xsd:NMTOKEN
#      xsd:NMTOKENS
#      xsd:NOTATION
#      xsd:Name
#      xsd:QName
#      xsd:anySimpleType
#      xsd:anyURI
#      xsd:base64Binary
#      xsd:boolean
#      xsd:byte
#      xsd:date
#      xsd:dateTime
#      xsd:decimal
#      xsd:double
#      xsd:duration
#      xsd:float
#      xsd:gDay
#      xsd:gMonth
#      xsd:gMonthDay
#      xsd:gYear
#      xsd:gYearMonth
#      xsd:hexBinary
#      xsd:int
#      xsd:integer
#      xsd:language
#      xsd:long
#      xsd:negativeInteger
#      xsd:nonNegativeInteger
#      xsd:nonPositiveInteger
#      xsd:normalizedString
#      xsd:positiveInteger
#      xsd:short
#      xsd:string
#      xsd:time
#      xsd:token
#      xsd:unsignedByte
#      xsd:unsignedInt
#      xsd:unsignedLong
#      xsd:unsignedShort
