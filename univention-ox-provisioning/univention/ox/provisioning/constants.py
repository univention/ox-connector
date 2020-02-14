import os
from pathlib import Path

__version__ = "1.0.1"

APP = "ox-connector"
DATA_DIR = Path("/var/lib/univention-appcenter/apps", APP, "data")
DEFAULT_CONTEXT = os.environ.get("OX/CONTEXT/ID", 10)
NEW_FILES_DIR = DATA_DIR / "listener"
OLD_FILES_DIR = NEW_FILES_DIR / "old"

# TODO: make parameter (AppSettings):
OX_SOAP_SERVER = os.environ.get("OX/SOAP/SERVER", "10.200.4.150")

# TODO: also make parameter (AppSettings):
# OX/CONTEXT/ID, OX/TIMEZONE, OX/CONTEXT/DEFAULT_QUOTA, OX/ADMINMASTER/PASSWORD
# OX/ADMINMASTER/USER, OX/SOAP/SERVER
# for use in appsuite/univention-ox-soap-api/modules/univention/ox/soap/config.py
