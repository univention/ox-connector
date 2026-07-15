# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023-2026 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20260702
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base


############# uv environment
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS uv
ARG UV_FROZEN=true

ADD --checksum=sha256:6426a73c3837e6e2483ee344cbc00f36394d179afcba6183cb77437e67db4af0 \
  https://github.com/astral-sh/uv/releases/download/0.11.26/uv-x86_64-unknown-linux-gnu.tar.gz \
  /tmp/uv.tar.gz

RUN tar -xz --strip-components=1 -C /usr/local/bin/ -f /tmp/uv.tar.gz && \
  rm -f /tmp/uv.tar.gz

WORKDIR /app

RUN \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3 \
  gcc \
  g++ \
  libpq-dev \
  python3-dev \
  libldap-dev \
  libsasl2-dev \
  libxslt-dev \
  libxml2-dev

COPY pyproject.toml ./
COPY uv.lock ./
COPY univention-ox-provisioning/ ./univention-ox-provisioning/
COPY univention-ox-soap-api/ ./univention-ox-soap-api/

RUN UV_FROZEN="${UV_FROZEN}" uv sync --no-editable --no-dev


############# uv dev env
FROM uv AS uv-dev
ARG UV_FROZEN=true

RUN UV_FROZEN="${UV_FROZEN}" uv sync --no-editable


############# udm translation files
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS translation

COPY udm/ /usr/local/share/ox-connector/resources/udm
RUN \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
    gettext && \
  msgfmt \
    /usr/local/share/ox-connector/resources/udm/hooks.d/de.po \
    -o /usr/local/share/ox-connector/resources/udm/hooks.d/de.mo && \
  msgfmt \
    /usr/local/share/ox-connector/resources/udm/syntax.d/de.po \
    -o /usr/local/share/ox-connector/resources/udm/syntax.d/de.mo && \
  msgfmt \
    /usr/local/share/ox-connector/resources/udm/handlers/oxmail/de.po \
    -o /usr/local/share/ox-connector/resources/udm/handlers/oxmail/de.mo && \
  msgfmt \
    /usr/local/share/ox-connector/resources/udm/handlers/oxresources/de.po \
    -o /usr/local/share/ox-connector/resources/udm/handlers/oxresources/de.mo


############# python runtime
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS runtime

ARG version

LABEL "org.opencontainers.image.title"="OX Connector" \
    "org.opencontainers.image.description"="OX Connector synchronizes entities from Univention Nubus to Open-Xchange" \
    "org.opencontainers.image.documentation"="https://docs.software-univention.de/n/de/docs/ox-connector-app.html#ox-connector-app" \
    "org.opencontainers.image.version"="$version"

RUN \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3 \
  libldap2 \
  libxslt1.1 \
  libxml2 \
  libpq5

COPY --from=uv /app/.venv/lib/python3.13/site-packages /usr/local/lib/python3.13/dist-packages/

COPY --from=translation /usr/local/share/ox-connector/resources/udm/hooks.d/de.mo /usr/local/share/ox-connector/resources/udm/hooks.d/de.mo
COPY --from=translation /usr/local/share/ox-connector/resources/udm/syntax.d/de.mo /usr/local/share/ox-connector/resources/udm/syntax.d/de.mo
COPY --from=translation /usr/local/share/ox-connector/resources/udm/handlers/oxmail/de.mo /usr/local/share/ox-connector/resources/udm/handlers/oxmail/de.mo
COPY --from=translation /usr/local/share/ox-connector/resources/udm/handlers/oxresources/de.mo /usr/local/share/ox-connector/resources/udm/handlers/oxresources/de.mo

RUN \
  python3 -c "from univention.ox.soap.services import get_ox_soap_service_class" && \
  python3 -c "from univention.ox.soap.backend_base import get_ox_integration_class" && \
  python3 -c "from univention.ox.provisioning import run"

COPY LICENSE /usr/local/share/ox-connector/LICENSE


############# final kubernetes image
FROM runtime AS k8s

# for entrypoint.sh
RUN \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  jq

WORKDIR /

COPY entrypoint.sh entrypoint.d/75-entrypoint.sh
COPY share/migrate_fupo_to_shared_account.py /usr/local/share/ox-connector/resources/migrate_fupo_to_shared_account.py
ENV PYTHONPATH="/:$PYTHONPATH"

COPY standalone-files/ /

CMD ["/usr/bin/python3", "/consumer.py"]


############# kubernetes image + tests
FROM k8s AS k8s-test

COPY --from=uv-dev /app/.venv/lib/python3.13/site-packages /usr/local/lib/python3.13/dist-packages/

COPY ./share/change_attribute_mapping.py /usr/local/share/ox-connector/resources/change_attribute_mapping.py
COPY tests /tests-env/tests


############# final appcenter image
FROM runtime AS appcenter

COPY share/ /usr/local/share/ox-connector/resources
COPY udm/ /usr/local/share/ox-connector/resources/udm
COPY umc/ /usr/local/share/ox-connector/resources/umc
COPY ldap/ /usr/local/share/ox-connector/resources/ldap

# see app/configure
RUN \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  ca-certificates

WORKDIR /

COPY --from=uv-dev /app/.venv/lib/python3.13/site-packages /usr/local/lib/python3.13/dist-packages/
COPY tests ./tests

ENTRYPOINT ["/bin/bash", "-c"]

CMD ["sleep infinity"]

# [EOF]
