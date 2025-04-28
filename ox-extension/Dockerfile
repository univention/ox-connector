# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.16.2-build-2025-04-24
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-521

######################
# Build Stage
######################
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build

RUN apt-get --assume-yes --no-install-recommends install gettext

COPY umc/ox-common.po /tmp/translations/
RUN mkdir -p /plugins/umc-i18n/de && \
    msgfmt /tmp/translations/ox-common.po -o /plugins/umc-i18n/de/ox-common.mo

######################
# Final Stage
######################
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}

WORKDIR /

# UDM hooks, syntax and handlers
COPY udm/handlers /plugins/udm-handlers
COPY udm/hooks.d /plugins/udm-hooks.d
COPY udm/syntax.d /plugins/udm-syntax.d
COPY udm/udm-data-loader /plugins/udm-data-loader

# UMC icons and module description
COPY umc/icons /plugins/umc-icons
COPY umc/ox-common.xml /plugins/umc-modules/

# Translations (from build stage)
COPY --from=build /plugins/umc-i18n /plugins/umc-i18n

# LDAP schemas
COPY ldap /plugins/ldap-schema

# Loader
COPY ox-extension/loader.sh /bin/loader

RUN adduser app
USER app

CMD ["/bin/loader"]
