#!/usr/bin/python3

import os.path
import re
from argparse import ArgumentParser, REMAINDER

from univention.ox.soap.config import save_context_admin_password, get_standard_context_admin_user, get_context_admin_user, NoContextAdminPassword, OX_MASTER_PASSWORD, OX_MASTER_ADMIN, CREDENTIALS_FILE

if not os.path.exists(CREDENTIALS_FILE):
    open(CREDENTIALS_FILE, "w").write("{}")

parser = ArgumentParser(
    description="Script that converts secret files found in the original OX App to a file the SOAP API client can digest")
parser.add_argument("secret_files", nargs=REMAINDER,
                    help="Secret files. Need to be in the form context${id}.secret and contain nothing but the password. Example: /etc/ox-secrets/context*.secret")
args = parser.parse_args()


context_admin = ""
if OX_MASTER_PASSWORD:
    context_id = "master"
    context_admin = OX_MASTER_ADMIN
    password = OX_MASTER_PASSWORD.strip()
    save_context_admin_password(context_id, context_admin, password)
    print("Master credentials successfully set")
else:
    print("Master credentials not set")


for fname in args.secret_files:
    if not os.path.exists(fname):
        continue

    context_id = re.search(r'context(\d+).secret', fname)
    if context_id is None:
        print(
            f"File {fname} does not fit the naming convention. Please make sure the filename fits this scheme: context[1-9][0-9]*.secret")
        continue
    context_id = context_id.group(1)
    try:
        get_context_admin_user(context_admin)
    except NoContextAdminPassword:
        context_admin = get_standard_context_admin_user(context_id)
    else:
        print(f"Context {context_id} already migrated. Skipping...")
        continue
    context_password = open(fname).read().strip()
    save_context_admin_password(context_id, context_admin, context_password)
    print(f"Context {context_id} successfully migrated")
