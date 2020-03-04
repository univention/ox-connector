# -*- coding: utf-8 -*-

#
# Use only Python 2 and 3 compatible code here!
#


import os

import setuptools

dir_here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(dir_here, "requirements.txt")) as fp:
    requirements = fp.read().splitlines()
version = os.environ["OX_PROVISIONING_VERSION"]

setuptools.setup(
    name="univention-ox-provisioning",
    version=version,
    author="Univention GmbH",
    author_email="packages@univention.de",
    description="Provision OX Users/Groups/Contexts/Resources using OX' SOAP API",
    url="https://www.univention.de/",
    install_requires=requirements,
    packages=["univention.ox.provisioning"],
    license="GNU Affero General Public License v3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
