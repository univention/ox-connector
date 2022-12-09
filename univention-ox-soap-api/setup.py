# -*- coding: utf-8 -*-

#
# Use only Python 2 and 3 compatible code here!
#


import os
import setuptools

UNIVENTION_OX_SOAP_API_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(UNIVENTION_OX_SOAP_API_ROOT, "requirements.txt")) as fp:
    requirements = fp.read().splitlines()

os.chdir("modules")  # to find 'modules'

setuptools.setup(
    name="univention-ox-soap-api",
    version=os.environ["OX_PROVISIONING_VERSION"],
    author="Univention GmbH",
    author_email="packages@univention.de",
    description="Library to access OX' SOAP API",
    url="https://www.univention.de/",
    install_requires=requirements,
    packages=["univention.ox.soap"],
    license="GNU Affero General Public License v3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
)
