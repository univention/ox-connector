# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

FROM alpine:3.14 AS final

ARG version

SHELL ["/bin/ash", "-euxo", "pipefail", "-c"]

WORKDIR /oxp

CMD ["/sbin/init"]

LABEL "description"="UCS OX provisioning app" \
    "version"="$version"

# init: Disable TTY spawning
RUN sed -i -e 's/^tty/# tty/g' /etc/inittab

# generate pip requirements
COPY univention-ox-soap-api/requirements.txt /build/requirements/ox-soap-api.txt
COPY univention-ox-provisioning/requirements.txt /build/requirements/ox-provisioning.txt
RUN set -o pipefail; find /build/requirements/ -name '*.txt' -exec cat {} + \
  | grep -E -v 'univention|six' \
  | sort \
  | uniq \
  > /build/requirements_all.txt \
 && rm -rf /build/requirements/

# package and Python dependency installation, base system configuration,
# and uninstallation - all in one step to keep image small
RUN apk add --no-cache \
    # build
    gcc~=10.3 \
    musl-dev~=1.2 \
    python3-dev~=3.9 \
    # runtime
    libxml2~=2.9 \
    libxslt~=1.1 \
    python3~=3.9 \
    tzdata~=2023c \
    ca-certificates~=20230506 \
    py3-pip~=20.3 \
    py3-lxml~=4.6 \
    py3-requests~=2.25 && \
  cp -v /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
  echo "Europe/Berlin" > /etc/timezone && \
  pip3 install --no-cache-dir --compile --upgrade \
    pip~=23.3 && \
  pip3 install --no-cache-dir --compile --upgrade \
    --requirement /build/requirements_all.txt && \
  apk del --no-cache \
    gcc \
    musl-dev \
    python3-dev && \
  python3 -c "from zeep import Client" && \
  rm -rf /tmp/*

COPY univention-ox-soap-api/ /tmp/univention-ox-soap-api/
RUN export OX_PROVISIONING_VERSION="$version" &&\
  pip3 install --no-cache-dir --compile --upgrade /tmp/univention-ox-soap-api && \
  python3 -c "from univention.ox.soap.services import get_ox_soap_service_class" && \
  python3 -c "from univention.ox.soap.backend_base import get_ox_integration_class" && \
  rm -rf /tmp/*

#RUN apk add py-spy  --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/

COPY univention-ox-provisioning /tmp/univention-ox-provisioning
COPY app/listener_trigger /tmp/app/
COPY tests /tmp/tests
COPY LICENSE /usr/local/share/ox-connector/LICENSE

WORKDIR /tmp

# 1st linting, then installation
# hadolint ignore=SC1091
RUN apk add --no-cache \
    gcc~=10.3 \
    python3-dev~=3.9 \
    musl-dev~=1.2 && \
  python3 -m venv --system-site-packages /tmp/venv && \
  . /tmp/venv/bin/activate && \
  pip3 install --no-cache-dir --compile --upgrade \
    pip~=23.3 && \
  pip3 install --no-cache-dir --compile \
    black~=24.1 \
	flake8~=7.0 \
	isort~=5.13 && \
  # deactivate() is not installed in 'ash' shell, manually deactivate virtualenv:
  export PATH="${_OLD_VIRTUAL_PATH:-}" && \
  export PS1="${_OLD_VIRTUAL_PS1:-}" && \
  # setup.py will read app version from environment
  export OX_PROVISIONING_VERSION="$version" && \
  pip3 install --no-cache-dir --compile /tmp/univention-ox-provisioning && \
  python3 -c "from univention.ox.provisioning import run" && \
  apk del --no-cache gcc python3-dev musl-dev && \
  rm -rf /tmp/*

COPY app/listener_trigger /usr/local/share/ox-connector/listener_trigger
COPY share/ /usr/local/share/ox-connector/resources
COPY udm/ /usr/local/share/ox-connector/resources/udm
COPY umc/ /usr/local/share/ox-connector/resources/umc
COPY ldap/ /usr/local/share/ox-connector/resources/ldap
COPY bin/* /usr/local/bin/

WORKDIR /oxp

###############################################################################
# A separate stage for tests
FROM final AS test

RUN apk add --no-cache vim~=8.2

RUN apk add --no-cache \
    py3-multidict~=5.1 \
    py3-yarl~=1.6 && \
  pip3 install --no-cache-dir --compile \
    udm-rest-client~=1.2 && \
  pip3 install --no-cache-dir --compile --index-url="https://test.pypi.org/simple/" \
    openapi-client-udm-ox~=1.0 && \
  python3 -c "from udm_rest_client.udm import UDM" && \
  python3 -c "import openapi_client_udm; openapi_client_udm.OxmailOxcontext.dn"

COPY share/check_sync_status.py /oxp/
COPY univention-ox-provisioning/requirements_tests.txt tests/ /oxp/tests/
RUN pip3 install --no-cache-dir --compile --upgrade -r /oxp/tests/requirements_tests.txt && \
  python3 -m pytest --collect-only /oxp/tests && \
  rm -rf /oxp/.pytest_cache /oxp/tests/requirements_tests.txt

# [EOF]
