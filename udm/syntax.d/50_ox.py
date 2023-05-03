import re

from univention.admin.syntax import select, simple, UDM_Objects



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
