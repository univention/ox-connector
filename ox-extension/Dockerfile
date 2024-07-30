# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.12.0
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}

# TODO: A sane user should be configured in the base image already.
RUN adduser app
USER app


WORKDIR /

# UDM hooks, syntax and handlers
COPY udm/handlers /plugins/udm-handlers
COPY udm/hooks.d /plugins/udm-hooks.d
COPY udm/syntax.d /plugins/udm-syntax.d
COPY udm/udm-data-loader /plugins/udm-data-loader

# UMC icons and po/xml
COPY umc/icons /plugins/umc-icons
COPY umc/ox-common.xml /plugins/umc-modules/

# LDAP schemas
COPY ldap /plugins/ldap-schema

COPY ox-extension/loader.sh /bin/loader

CMD ["/bin/loader"]
