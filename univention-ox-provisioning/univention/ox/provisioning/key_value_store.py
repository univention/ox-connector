#
# Copyright 2024-2025 Univention GmbH
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

import dbm.gnu
from contextlib import contextmanager


class KeyValueStore(object):
    """
    Database about meta information on this listener.
    Particularly the number of consecutive errors.
    """

    def __init__(self, db_file):
        self.db_fname = db_file
        self.data = {}
        self.changes = set()
        with self.open() as data_base:
            for k in data_base.keys():
                self.data[k.decode("UTF-8").lower()] = data_base[k].decode(
                    "UTF-8",
                )

    @contextmanager
    def open(self, flags="cs"):
        """Open DBM-Database and yield the handler"""
        with dbm.gnu.open(self.db_fname, flags) as data_base:
            yield data_base

    def set(self, distinguished_name, path):
        """Write item to DBM-Database"""
        if distinguished_name is None:
            return
        distinguished_name = distinguished_name.lower()
        if path is None:
            self.data[distinguished_name] = None
        else:
            self.data[distinguished_name] = str(path)
        self.changes.add(distinguished_name)

    def unset(self, distinguished_name):
        """Remove item from DBM-Database"""
        self.set(distinguished_name, None)

    def get(self, key):
        """Read value from DBM-Database"""
        return self.data.get(key.lower())

    def commit(self):
        with self.open(flags="cs") as data_base:
            for dn in self.changes:
                v = self.data[dn]
                if v:
                    data_base[dn] = v
                elif dn in data_base:
                    del data_base[dn]


def get_old_db():
    return KeyValueStore(
        "/var/lib/univention-appcenter/apps/ox-connector/data/listener/old.db",
    )
