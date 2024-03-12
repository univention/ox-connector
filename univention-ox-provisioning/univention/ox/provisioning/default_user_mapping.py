#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Univention GmbH
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

from typing import List, Optional


class SpecialHandling:
    DEFAULT = "DEFAULT"
    IMAGE = "IMAGE"
    DATE = "DATE"
    IMAP_URL = "IMAP_URL"
    SMTP_URL = "SMTP_URL"

class Mapping(dict):
    def __init__(
        self,
        ldap_attribute: str,
        nillable: bool = True,
        multi_value: bool = False,
        special_handling: SpecialHandling = SpecialHandling.DEFAULT,
        alternative_attributes: List[str] = [],
        position: Optional[int] = None,
    ):
        dict.__init__(
            self,
            ldap_attribute=ldap_attribute,
            nillable=nillable,
            multi_value=multi_value,
            special_handling=special_handling,
            alternative_attributes=alternative_attributes,
            position=position,
        )

DEFAULT_USER_MAPPING = {    "display_name": Mapping("oxDisplayName", alternative_attributes=["displayName"]),
    "given_name": Mapping("firstname"),
    "sur_name": Mapping("lastname"),
    "email1": Mapping("mailPrimaryAddress", nillable=False),
    "branches": Mapping("oxBranches"),
    "cellular_telephone1": Mapping("oxMobileBusiness"),
    "city_business": Mapping("city"),
    "city_home": Mapping("oxCityHome"),
    "city_other": Mapping("oxCityOther"),
    "commercial_register": Mapping("oxCommercialRegister"),
    "company": Mapping("organisation"),
    "country_business": Mapping("oxCountryBusiness"),
    "country_home": Mapping("oxCountryHome"),
    "country_other": Mapping("oxCountryOther"),
    "department": Mapping("oxDepartment"),
    "email2": Mapping("oxEmail2"),
    "email3": Mapping("oxEmail3"),
    "employee_type": Mapping("employeeType"),
    "fax_business": Mapping("oxFaxBusiness"),
    "fax_home": Mapping("oxFaxHome"),
    "fax_other": Mapping("oxFaxOther"),
    "instant_messenger1": Mapping("oxInstantMessenger1"),
    "instant_messenger2": Mapping("oxInstantMessenger2"),
    "manager_name": Mapping("oxManagerName"),
    "marital_status": Mapping("oxMarialStatus"),
    "middle_name": Mapping("oxMiddleName"),
    "nickname": Mapping("oxNickName"),
    "note": Mapping("oxNote"),
    "number_of_children": Mapping("oxNumOfChildren"),
    "number_of_employee": Mapping("employeeNumber"),
    "position": Mapping("oxPosition"),
    "postal_code_business": Mapping("postcode"),
    "postal_code_home": Mapping("oxPostalCodeHome"),
    "postal_code_other": Mapping("oxPostalCodeOther"),
    "profession": Mapping("oxProfession"),
    "sales_volume": Mapping("oxSalesVolume"),
    "spouse_name": Mapping("oxSpouseName"),
    "state_business": Mapping("oxStateBusiness"),
    "state_home": Mapping("oxStateHome"),
    "state_other": Mapping("oxStateOther"),
    "street_business": Mapping("street"),
    "street_home": Mapping("oxStreetHome"),
    "street_other": Mapping("oxStreetOther"),
    "suffix": Mapping("oxSuffix"),
    "tax_id": Mapping("oxTaxId"),
    "telephone_assistant": Mapping("oxTelephoneAssistant"),
    "telephone_car": Mapping("oxTelephoneCar"),
    "telephone_company": Mapping("oxTelephoneCompany"),
    "telephone_ip": Mapping("oxTelephoneIp"),
    "telephone_other": Mapping("oxTelephoneOther"),
    "telephone_telex": Mapping("oxTelephoneTelex"),
    "telephone_ttytdd": Mapping("oxTelephoneTtydd"),
    "title": Mapping("title"),
    "url": Mapping("oxUrl"),
    "used_quota": Mapping("oxUserQuota"),
    "max_quota": Mapping("oxUserQuota"),
    "userfield01": Mapping("oxUserfield01"),
    "userfield02": Mapping("oxUserfield02"),
    "userfield03": Mapping("oxUserfield03"),
    "userfield04": Mapping("oxUserfield04"),
    "userfield05": Mapping("oxUserfield05"),
    "userfield06": Mapping("oxUserfield06"),
    "userfield07": Mapping("oxUserfield07"),
    "userfield08": Mapping("oxUserfield08"),
    "userfield09": Mapping("oxUserfield09"),
    "userfield10": Mapping("oxUserfield10"),
    "userfield11": Mapping("oxUserfield11"),
    "userfield12": Mapping("oxUserfield12"),
    "userfield13": Mapping("oxUserfield13"),
    "userfield14": Mapping("oxUserfield14"),
    "userfield15": Mapping("oxUserfield15"),
    "userfield16": Mapping("oxUserfield16"),
    "userfield17": Mapping("oxUserfield17"),
    "userfield18": Mapping("oxUserfield18"),
    "userfield19": Mapping("oxUserfield19"),
    "userfield20": Mapping("oxUserfield20"),
    "image1": Mapping("jpegPhoto", special_handling=SpecialHandling.IMAGE),
    "room_number": Mapping("roomNumber"),
    "cellular_telephone2": Mapping("mobileTelephoneNumber"),
    "telephone_pager": Mapping("pagerTelephoneNumber"),
    "anniversary": Mapping("oxAnniversary", special_handling=SpecialHandling.DATE),
    "birthday": Mapping("birthday", special_handling=SpecialHandling.DATE),
    "telephone_business1": Mapping("phone", position=0),
    "telephone_business2": Mapping("phone", position=1),
    "telephone_home1": Mapping("homeTelephoneNumber", position=0),
    "telephone_home2": Mapping("homeTelephoneNumber", position=1),
    "imap_server": Mapping("mailHomeServer", special_handling=SpecialHandling.IMAP_URL),
    "smtp_server": Mapping("mailHomeServer", special_handling=SpecialHandling.SMTP_URL),
    "aliases": Mapping("mailAlternativeAddress", multi_value=True)
}