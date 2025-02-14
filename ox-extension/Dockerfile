# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.14.0-build-2024-12-12
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}

# TODO: See below
# RUN apt-get --assume-yes --verbose-versions --no-install-recommends install \
#     gettext && \
#     rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

WORKDIR /

# UDM hooks, syntax and handlers
COPY udm/handlers /plugins/udm-handlers
COPY udm/hooks.d /plugins/udm-hooks.d
COPY udm/syntax.d /plugins/udm-syntax.d
COPY udm/udm-data-loader /plugins/udm-data-loader

# UMC icons and po/xml
COPY umc/icons /plugins/umc-icons
COPY umc/ox-common.xml /plugins/umc-modules/

# TODO: Translation files need to go into /usr/share/univention-management-console/i18n
# which we do not mount at the moment into the umc-server.
# RUN mkdir -p /tmp/translations /plugins/umc-modules/i18n
# COPY udm/handlers/oxmail/de.po /tmp/translations/oxmail.po
# COPY udm/handlers/oxresources/de.po /tmp/translations/oxresources.po
# RUN msgcat --use-first /tmp/translations/oxmail.po /tmp/translations/oxresources.po -o /tmp/translations/merged.po
# RUN msgfmt /tmp/translations/merged.po -o /plugins/umc-modules/i18n/ox-common.mo
# RUN rm -rf /tmp/translations

# LDAP schemas
COPY ldap /plugins/ldap-schema

COPY ox-extension/loader.sh /bin/loader

RUN adduser app
USER app

CMD ["/bin/loader"]
