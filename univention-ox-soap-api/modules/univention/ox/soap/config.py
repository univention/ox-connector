import os
import random
import string
import json
try:
    from typing import Dict, Optional, Tuple, Union
except ImportError:
    pass

DEFAULT_IMAP_SERVER = os.environ.get("OX_IMAP_SERVER", "imap://localhost:143")
DEFAULT_SMTP_SERVER = os.environ.get("OX_SMTP_SERVER", "smtp://localhost:587")
DEFAULT_CONTEXT = int(os.environ.get("DEFAULT_CONTEXT", 10))
DEFAULT_LANGUAGE = os.environ.get("OX_LANGUAGE", "de_DE")
DOMAIN = os.environ.get("DOMAINNAME", "localhost.localdomain")
IMAP_LOGIN = os.environ.get("OX_IMAP_LOGIN", "{}")
LOCAL_TIMEZONE = os.environ.get("LOCAL_TIMEZONE", "Europe/Berlin")
OX_MASTER_ADMIN = os.environ.get("OX_MASTER_ADMIN", "oxadminmaster")
OX_MASTER_PASSWORD = os.environ.get("OX_MASTER_PASSWORD", "")
QUOTA = -1  # unlimited
OX_SOAP_SERVER = os.environ.get("OX_SOAP_SERVER", "http://127.0.0.1")
CREDENTIALS_FILE = os.environ.get(
    "OX_CREDENTIALS_FILE", "/etc/ox-secrets/ox-contexts.json")
FUNCTIONAL_ACCOUNT_LOGIN = os.environ.get(
    "OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE")
if not FUNCTIONAL_ACCOUNT_LOGIN:
    FUNCTIONAL_ACCOUNT_LOGIN = "{{fa_entry_uuid}}{{username}}"

_CREDENTIALS = {}


class NoContextAdminPassword(Exception):
    pass


def get_new_context_attributes(context_id):  # type: (int) -> Dict[str, str]
    name = 'context{}'.format(context_id)
    mapping = ['context{}'.format(context_id), str(context_id)]
    return {
        'id': context_id,
        'name': name,
        'mapping': mapping,
        'timezone': LOCAL_TIMEZONE,
        'username': get_standard_context_admin_user(context_id),
        'displayname': 'OX Admin',
        'givenname': 'OX',
        'surname': 'Admin',
        'email': '{}@{}'.format(get_standard_context_admin_user(context_id), DOMAIN),
        'quota': QUOTA,
        'password': get_random_password(),
    }


def get_random_password(length=64):  # type: (Optional[int]) -> str
    pw = list()
    if length >= 3:
        pw.append(random.choice(string.ascii_lowercase))
        pw.append(random.choice(string.ascii_uppercase))
        pw.append(random.choice(string.digits))
        length -= len(pw)
    pw.extend(random.choice(string.ascii_letters + string.digits)
              for _x in range(length))
    random.shuffle(pw)
    return ''.join(pw)


def _get_credentials():
    if not _CREDENTIALS:
        with open(CREDENTIALS_FILE, 'r') as fd:
            _CREDENTIALS.update(json.load(fd))
    return _CREDENTIALS


def _save_credentials(credentials):
    with open(CREDENTIALS_FILE, "w") as fd:
        os.chmod(fd.name, 0o600)
        json.dump(credentials, fd, sort_keys=True, indent=2)


def get_context_admin_user(context_id):  # type: (Union[int, str]) -> str
    credentials = _get_credentials()
    try:
        return credentials[str(context_id)]["adminuser"]
    except KeyError:
        raise NoContextAdminPassword(context_id)


def get_context_admin_password(context_id):  # type: (Union[int, str]) -> str
    credentials = _get_credentials()
    try:
        return credentials[str(context_id)]["adminpass"]
    except KeyError:
        raise NoContextAdminPassword(context_id)


def get_standard_context_admin_user(context_id):
    # type: (Union[int, str]) -> str
    if int(context_id) == DEFAULT_CONTEXT:
        return 'oxadmin'
    else:
        return 'oxadmin-context{}'.format(context_id)


def save_context_admin_password(context_id, context_admin, password):
    # type: (Union[int, str], str, str) -> None
    credentials = _get_credentials()
    credentials[str(context_id)] = {
        "adminuser": context_admin,
        "adminpass": password,
    }
    _save_credentials(credentials)


def remove_context_admin_password(context_id):
    # type: (Union[int, str]) -> None
    credentials = _get_credentials()
    try:
        del credentials[str(context_id)]
    except KeyError:
        pass
    else:
        _save_credentials(credentials)


# type: (Union[int, str]) -> Tuple[str, str]
def get_credentials_for_context(context_id):
    admuser = get_context_admin_user(context_id)
    admpass = get_context_admin_password(context_id)
    return admuser, admpass


def get_master_credentials():  # type: () -> Tuple[str, str]
    return get_credentials_for_context("master")
