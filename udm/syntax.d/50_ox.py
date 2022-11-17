import re

from univention.admin.syntax import select, simple, UDM_Objects


class oxDriveBool(select):
	name = 'oxDriveBool'
	choices = [
		('1', 'enabled (requires groupware permission)'),
		('0', 'disabled'),
	]


class ExtendedAttributeIntegerType(univention.admin.types.TypeHint):
	_python_types = (int,  string)
	_openapi_type = 'integer'

	def decode_value(self, value):
		try:
			value = int(value)
		except ValueError:
			ud.debug(ud.ADMIN, ud.WARN, '%s: %s: not a integer: %r' % (self.property_name, self.syntax.name, value,))
		return value

	def encode_value(self, value):
		if isinstance(value, int):
			value = str(value).encode()
		return value


class oxContextSelect(UDM_Objects):
	udm_modules = ('oxmail/oxcontext', )
	type_class = ExtendedAttributeIntegerType
	label = '%(name)s'
	key = '%(contextid)s'
	regex = None

	@classmethod
	def parse(self, text):
		if isinstance(text, int):
			return [text]
		elif isinstance(text, (bytes, str)):
			return [int(text)]
		elif isinstance(text, list) and len(text) == 1:
			return [int(text[0])]
		else:
			raise ValueError("Can't parse %s of type %s as an int" % (text, type(text)))


class oxaccess(UDM_Objects):
	udm_modules = ('oxmail/accessprofile', )
	label = '%(displayName)s'
	key = '%(name)s'
	regex = None


class oxlanguage(select):
	name = 'oxlanguage'
	choices = [
		('cs_CZ', 'Czech/Czech Republic'),
		('de_DE', 'German/Germany'),
		('en_GB', 'English/UK'),
		('en_US', 'English/US'),
		('es_ES', 'Spanish/Spain'),
		('fr_FR', 'French/France'),
		('hu_HU', 'Hungarian/Hungary'),
		('it_IT', 'Italian/Italy'),
		('ja_JP', 'Japanese/Japan'),
		('lv_LV', 'Latvian/Latvia'),
		('nl_NL', 'Dutch/Netherlands'),
		('pl_PL', 'Polish/Poland'),
		('sk_SK', 'Slovak/Slovakia'),
		('zh_CN', 'Chinese/China'),
		('zh_TW', 'Chinese/Taiwan, Province of China'),
	]


class oxtimezone(select):
	name = 'oxtimezone'
	choices = [
		('Africa/Abidjan', 'Africa/Abidjan'),
		('Africa/Accra', 'Africa/Accra'),
		('Africa/Addis_Ababa', 'Africa/Addis_Ababa'),
		('Africa/Algiers', 'Africa/Algiers'),
		('Africa/Asmera', 'Africa/Asmera'),
		('Africa/Bangui', 'Africa/Bangui'),
		('Africa/Banjul', 'Africa/Banjul'),
		('Africa/Bissau', 'Africa/Bissau'),
		('Africa/Blantyre', 'Africa/Blantyre'),
		('Africa/Bujumbura', 'Africa/Bujumbura'),
		('Africa/Cairo', 'Africa/Cairo'),
		('Africa/Casablanca', 'Africa/Casablanca'),
		('Africa/Conakry', 'Africa/Conakry'),
		('Africa/Dakar', 'Africa/Dakar'),
		('Africa/Dar_es_Salaam', 'Africa/Dar_es_Salaam'),
		('Africa/Djibouti', 'Africa/Djibouti'),
		('Africa/Douala', 'Africa/Douala'),
		('Africa/Freetown', 'Africa/Freetown'),
		('Africa/Gaborone', 'Africa/Gaborone'),
		('Africa/Harare', 'Africa/Harare'),
		('Africa/Johannesburg', 'Africa/Johannesburg'),
		('Africa/Kampala', 'Africa/Kampala'),
		('Africa/Khartoum', 'Africa/Khartoum'),
		('Africa/Kigali', 'Africa/Kigali'),
		('Africa/Kinshasa', 'Africa/Kinshasa'),
		('Africa/Lagos', 'Africa/Lagos'),
		('Africa/Libreville', 'Africa/Libreville'),
		('Africa/Lome', 'Africa/Lome'),
		('Africa/Luanda', 'Africa/Luanda'),
		('Africa/Lubumbashi', 'Africa/Lubumbashi'),
		('Africa/Lusaka', 'Africa/Lusaka'),
		('Africa/Malabo', 'Africa/Malabo'),
		('Africa/Maputo', 'Africa/Maputo'),
		('Africa/Maseru', 'Africa/Maseru'),
		('Africa/Mbabane', 'Africa/Mbabane'),
		('Africa/Mogadishu', 'Africa/Mogadishu'),
		('Africa/Monrovia', 'Africa/Monrovia'),
		('Africa/Nairobi', 'Africa/Nairobi'),
		('Africa/Ndjamena', 'Africa/Ndjamena'),
		('Africa/Niamey', 'Africa/Niamey'),
		('Africa/Nouakchott', 'Africa/Nouakchott'),
		('Africa/Ouagadougou', 'Africa/Ouagadougou'),
		('Africa/Porto-Novo', 'Africa/Porto-Novo'),
		('Africa/Sao_Tome', 'Africa/Sao_Tome'),
		('Africa/Timbuktu', 'Africa/Timbuktu'),
		('Africa/Tripoli', 'Africa/Tripoli'),
		('Africa/Tunis', 'Africa/Tunis'),
		('Africa/Windhoek', 'Africa/Windhoek'),
		('America/Adak', 'America/Adak'),
		('America/Anchorage', 'America/Anchorage'),
		('America/Anguilla', 'America/Anguilla'),
		('America/Antigua', 'America/Antigua'),
		('America/Aruba', 'America/Aruba'),
		('America/Asuncion', 'America/Asuncion'),
		('America/Barbados', 'America/Barbados'),
		('America/Belize', 'America/Belize'),
		('America/Bogota', 'America/Bogota'),
		('America/Buenos_Aires', 'America/Buenos_Aires'),
		('America/Caracas', 'America/Caracas'),
		('America/Cayenne', 'America/Cayenne'),
		('America/Cayman', 'America/Cayman'),
		('America/Chicago', 'America/Chicago'),
		('America/Costa_Rica', 'America/Costa_Rica'),
		('America/Cuiaba', 'America/Cuiaba'),
		('America/Curacao', 'America/Curacao'),
		('America/Dawson_Creek', 'America/Dawson_Creek'),
		('America/Denver', 'America/Denver'),
		('America/Dominica', 'America/Dominica'),
		('America/Edmonton', 'America/Edmonton'),
		('America/El_Salvador', 'America/El_Salvador'),
		('America/Fortaleza', 'America/Fortaleza'),
		('America/Godthab', 'America/Godthab'),
		('America/Grand_Turk', 'America/Grand_Turk'),
		('America/Grenada', 'America/Grenada'),
		('America/Guadeloupe', 'America/Guadeloupe'),
		('America/Guatemala', 'America/Guatemala'),
		('America/Guayaquil', 'America/Guayaquil'),
		('America/Guyana', 'America/Guyana'),
		('America/Halifax', 'America/Halifax'),
		('America/Havana', 'America/Havana'),
		('America/Indianapolis', 'America/Indianapolis'),
		('America/Jamaica', 'America/Jamaica'),
		('America/La_Paz', 'America/La_Paz'),
		('America/Lima', 'America/Lima'),
		('America/Los_Angeles', 'America/Los_Angeles'),
		('America/Managua', 'America/Managua'),
		('America/Manaus', 'America/Manaus'),
		('America/Martinique', 'America/Martinique'),
		('America/Mazatlan', 'America/Mazatlan'),
		('America/Mexico_City', 'America/Mexico_City'),
		('America/Miquelon', 'America/Miquelon'),
		('America/Montevideo', 'America/Montevideo'),
		('America/Montreal', 'America/Montreal'),
		('America/Montserrat', 'America/Montserrat'),
		('America/Nassau', 'America/Nassau'),
		('America/New_York', 'America/New_York'),
		('America/Noronha', 'America/Noronha'),
		('America/Panama', 'America/Panama'),
		('America/Paramaribo', 'America/Paramaribo'),
		('America/Phoenix', 'America/Phoenix'),
		('America/Port-au-Prince', 'America/Port-au-Prince'),
		('America/Port_of_Spain', 'America/Port_of_Spain'),
		('America/Porto_Acre', 'America/Porto_Acre'),
		('America/Puerto_Rico', 'America/Puerto_Rico'),
		('America/Regina', 'America/Regina'),
		('America/Rio_Branco', 'America/Rio_Branco'),
		('America/Santiago', 'America/Santiago'),
		('America/Santo_Domingo', 'America/Santo_Domingo'),
		('America/Sao_Paulo', 'America/Sao_Paulo'),
		('America/Scoresbysund', 'America/Scoresbysund'),
		('America/St_Johns', 'America/St_Johns'),
		('America/St_Kitts', 'America/St_Kitts'),
		('America/St_Lucia', 'America/St_Lucia'),
		('America/St_Thomas', 'America/St_Thomas'),
		('America/St_Vincent', 'America/St_Vincent'),
		('America/Tegucigalpa', 'America/Tegucigalpa'),
		('America/Thule', 'America/Thule'),
		('America/Tijuana', 'America/Tijuana'),
		('America/Tortola', 'America/Tortola'),
		('America/Vancouver', 'America/Vancouver'),
		('America/Winnipeg', 'America/Winnipeg'),
		('Antarctica/Casey', 'Antarctica/Casey'),
		('Antarctica/DumontDUrville', 'Antarctica/DumontDUrville'),
		('Antarctica/Mawson', 'Antarctica/Mawson'),
		('Antarctica/McMurdo', 'Antarctica/McMurdo'),
		('Antarctica/Palmer', 'Antarctica/Palmer'),
		('Asia/Aden', 'Asia/Aden'),
		('Asia/Almaty', 'Asia/Almaty'),
		('Asia/Amman', 'Asia/Amman'),
		('Asia/Anadyr', 'Asia/Anadyr'),
		('Asia/Aqtau', 'Asia/Aqtau'),
		('Asia/Aqtobe', 'Asia/Aqtobe'),
		('Asia/Ashkhabad', 'Asia/Ashkhabad'),
		('Asia/Baghdad', 'Asia/Baghdad'),
		('Asia/Bahrain', 'Asia/Bahrain'),
		('Asia/Baku', 'Asia/Baku'),
		('Asia/Bangkok', 'Asia/Bangkok'),
		('Asia/Beirut', 'Asia/Beirut'),
		('Asia/Bishkek', 'Asia/Bishkek'),
		('Asia/Brunei', 'Asia/Brunei'),
		('Asia/Calcutta', 'Asia/Calcutta'),
		('Asia/Colombo', 'Asia/Colombo'),
		('Asia/Dacca', 'Asia/Dacca'),
		('Asia/Damascus', 'Asia/Damascus'),
		('Asia/Dhaka', 'Asia/Dhaka'),
		('Asia/Dubai', 'Asia/Dubai'),
		('Asia/Dushanbe', 'Asia/Dushanbe'),
		('Asia/Hong_Kong', 'Asia/Hong_Kong'),
		('Asia/Irkutsk', 'Asia/Irkutsk'),
		('Asia/Jakarta', 'Asia/Jakarta'),
		('Asia/Jayapura', 'Asia/Jayapura'),
		('Asia/Jerusalem', 'Asia/Jerusalem'),
		('Asia/Kabul', 'Asia/Kabul'),
		('Asia/Kamchatka', 'Asia/Kamchatka'),
		('Asia/Karachi', 'Asia/Karachi'),
		('Asia/Katmandu', 'Asia/Katmandu'),
		('Asia/Krasnoyarsk', 'Asia/Krasnoyarsk'),
		('Asia/Kuala_Lumpur', 'Asia/Kuala_Lumpur'),
		('Asia/Kuwait', 'Asia/Kuwait'),
		('Asia/Macao', 'Asia/Macao'),
		('Asia/Magadan', 'Asia/Magadan'),
		('Asia/Manila', 'Asia/Manila'),
		('Asia/Muscat', 'Asia/Muscat'),
		('Asia/Nicosia', 'Asia/Nicosia'),
		('Asia/Novosibirsk', 'Asia/Novosibirsk'),
		('Asia/Phnom_Penh', 'Asia/Phnom_Penh'),
		('Asia/Pyongyang', 'Asia/Pyongyang'),
		('Asia/Qatar', 'Asia/Qatar'),
		('Asia/Rangoon', 'Asia/Rangoon'),
		('Asia/Riyadh', 'Asia/Riyadh'),
		('Asia/Saigon', 'Asia/Saigon'),
		('Asia/Seoul', 'Asia/Seoul'),
		('Asia/Shanghai', 'Asia/Shanghai'),
		('Asia/Singapore', 'Asia/Singapore'),
		('Asia/Taipei', 'Asia/Taipei'),
		('Asia/Tashkent', 'Asia/Tashkent'),
		('Asia/Tbilisi', 'Asia/Tbilisi'),
		('Asia/Tehran', 'Asia/Tehran'),
		('Asia/Thimbu', 'Asia/Thimbu'),
		('Asia/Tokyo', 'Asia/Tokyo'),
		('Asia/Ujung_Pandang', 'Asia/Ujung_Pandang'),
		('Asia/Ulaanbaatar', 'Asia/Ulaanbaatar'),
		('Asia/Vientiane', 'Asia/Vientiane'),
		('Asia/Vladivostok', 'Asia/Vladivostok'),
		('Asia/Yakutsk', 'Asia/Yakutsk'),
		('Asia/Yekaterinburg', 'Asia/Yekaterinburg'),
		('Asia/Yerevan', 'Asia/Yerevan'),
		('Atlantic/Azores', 'Atlantic/Azores'),
		('Atlantic/Bermuda', 'Atlantic/Bermuda'),
		('Atlantic/Canary', 'Atlantic/Canary'),
		('Atlantic/Cape_Verde', 'Atlantic/Cape_Verde'),
		('Atlantic/Faeroe', 'Atlantic/Faeroe'),
		('Atlantic/Jan_Mayen', 'Atlantic/Jan_Mayen'),
		('Atlantic/Reykjavik', 'Atlantic/Reykjavik'),
		('Atlantic/South_Georgia', 'Atlantic/South_Georgia'),
		('Atlantic/St_Helena', 'Atlantic/St_Helena'),
		('Atlantic/Stanley', 'Atlantic/Stanley'),
		('Australia/Adelaide', 'Australia/Adelaide'),
		('Australia/Brisbane', 'Australia/Brisbane'),
		('Australia/Broken_Hill', 'Australia/Broken_Hill'),
		('Australia/Darwin', 'Australia/Darwin'),
		('Australia/Hobart', 'Australia/Hobart'),
		('Australia/Lord_Howe', 'Australia/Lord_Howe'),
		('Australia/Perth', 'Australia/Perth'),
		('Australia/Sydney', 'Australia/Sydney'),
		('Europe/Amsterdam', 'Europe/Amsterdam'),
		('Europe/Andorra', 'Europe/Andorra'),
		('Europe/Athens', 'Europe/Athens'),
		('Europe/Belgrade', 'Europe/Belgrade'),
		('Europe/Berlin', 'Europe/Berlin'),
		('Europe/Brussels', 'Europe/Brussels'),
		('Europe/Bucharest', 'Europe/Bucharest'),
		('Europe/Budapest', 'Europe/Budapest'),
		('Europe/Chisinau', 'Europe/Chisinau'),
		('Europe/Copenhagen', 'Europe/Copenhagen'),
		('Europe/Dublin', 'Europe/Dublin'),
		('Europe/Gibraltar', 'Europe/Gibraltar'),
		('Europe/Helsinki', 'Europe/Helsinki'),
		('Europe/Istanbul', 'Europe/Istanbul'),
		('Europe/Kaliningrad', 'Europe/Kaliningrad'),
		('Europe/Kiev', 'Europe/Kiev'),
		('Europe/Lisbon', 'Europe/Lisbon'),
		('Europe/London', 'Europe/London'),
		('Europe/Luxembourg', 'Europe/Luxembourg'),
		('Europe/Madrid', 'Europe/Madrid'),
		('Europe/Malta', 'Europe/Malta'),
		('Europe/Minsk', 'Europe/Minsk'),
		('Europe/Monaco', 'Europe/Monaco'),
		('Europe/Moscow', 'Europe/Moscow'),
		('Europe/Oslo', 'Europe/Oslo'),
		('Europe/Paris', 'Europe/Paris'),
		('Europe/Prague', 'Europe/Prague'),
		('Europe/Riga', 'Europe/Riga'),
		('Europe/Rome', 'Europe/Rome'),
		('Europe/Samara', 'Europe/Samara'),
		('Europe/Simferopol', 'Europe/Simferopol'),
		('Europe/Sofia', 'Europe/Sofia'),
		('Europe/Stockholm', 'Europe/Stockholm'),
		('Europe/Tallinn', 'Europe/Tallinn'),
		('Europe/Tirane', 'Europe/Tirane'),
		('Europe/Vaduz', 'Europe/Vaduz'),
		('Europe/Vienna', 'Europe/Vienna'),
		('Europe/Vilnius', 'Europe/Vilnius'),
		('Europe/Warsaw', 'Europe/Warsaw'),
		('Europe/Zurich', 'Europe/Zurich'),
		('GMT', 'GMT'),
		('Indian/Antananarivo', 'Indian/Antananarivo'),
		('Indian/Chagos', 'Indian/Chagos'),
		('Indian/Christmas', 'Indian/Christmas'),
		('Indian/Cocos', 'Indian/Cocos'),
		('Indian/Comoro', 'Indian/Comoro'),
		('Indian/Kerguelen', 'Indian/Kerguelen'),
		('Indian/Mahe', 'Indian/Mahe'),
		('Indian/Maldives', 'Indian/Maldives'),
		('Indian/Mauritius', 'Indian/Mauritius'),
		('Indian/Mayotte', 'Indian/Mayotte'),
		('Indian/Reunion', 'Indian/Reunion'),
		('Pacific/Apia', 'Pacific/Apia'),
		('Pacific/Auckland', 'Pacific/Auckland'),
		('Pacific/Chatham', 'Pacific/Chatham'),
		('Pacific/Easter', 'Pacific/Easter'),
		('Pacific/Efate', 'Pacific/Efate'),
		('Pacific/Enderbury', 'Pacific/Enderbury'),
		('Pacific/Fakaofo', 'Pacific/Fakaofo'),
		('Pacific/Fiji', 'Pacific/Fiji'),
		('Pacific/Funafuti', 'Pacific/Funafuti'),
		('Pacific/Galapagos', 'Pacific/Galapagos'),
		('Pacific/Gambier', 'Pacific/Gambier'),
		('Pacific/Guadalcanal', 'Pacific/Guadalcanal'),
		('Pacific/Guam', 'Pacific/Guam'),
		('Pacific/Honolulu', 'Pacific/Honolulu'),
		('Pacific/Kiritimati', 'Pacific/Kiritimati'),
		('Pacific/Kosrae', 'Pacific/Kosrae'),
		('Pacific/Majuro', 'Pacific/Majuro'),
		('Pacific/Marquesas', 'Pacific/Marquesas'),
		('Pacific/Nauru', 'Pacific/Nauru'),
		('Pacific/Niue', 'Pacific/Niue'),
		('Pacific/Norfolk', 'Pacific/Norfolk'),
		('Pacific/Noumea', 'Pacific/Noumea'),
		('Pacific/Pago_Pago', 'Pacific/Pago_Pago'),
		('Pacific/Palau', 'Pacific/Palau'),
		('Pacific/Pitcairn', 'Pacific/Pitcairn'),
		('Pacific/Ponape', 'Pacific/Ponape'),
		('Pacific/Port_Moresby', 'Pacific/Port_Moresby'),
		('Pacific/Rarotonga', 'Pacific/Rarotonga'),
		('Pacific/Saipan', 'Pacific/Saipan'),
		('Pacific/Tahiti', 'Pacific/Tahiti'),
		('Pacific/Tarawa', 'Pacific/Tarawa'),
		('Pacific/Tongatapu', 'Pacific/Tongatapu'),
		('Pacific/Truk', 'Pacific/Truk'),
		('Pacific/Wake', 'Pacific/Wake'),
		('Pacific/Wallis', 'Pacific/Wallis'),
		('UTC', 'UTC'),
		('WET', 'WET'),
	]


class gid_ox(simple):
	name = 'gid_ox'
	min_length = 1
	max_length = 32
	_re = re.compile(r'(?u)^\w([\w -.]*\w)?$')
	_re = re.compile(r'(?u)(^[a-zA-Z])[a-zA-Z0-9._ -]*([a-zA-Z0-9]$)')

	@classmethod
	def parse(cls, text):
		unicode_text = text.decode("utf-8") if isinstance(text, bytes) else text
		if cls._re.match(unicode_text):
			return text
		else:
			raise univention.admin.uexceptions.valueError(
				"A group name must start and end with a letter, number or underscore. In between additionally spaces, "
				"dashes and dots are allowed."
			)
