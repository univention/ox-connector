FROM alpine:3.14

ARG version

SHELL ["/bin/sh", "-euxo", "pipefail", "-c"]

WORKDIR /oxp

CMD ["/sbin/init"]

LABEL "description"="UCS OX provisioning app" \
    "version"="$version"

# init: Disable TTY spawning
RUN sed -i -e 's/^tty/# tty/g' /etc/inittab

# generate pip requirements
COPY univention-ox-soap-api/requirements.txt /build/requirements/ox-soap-api.txt
COPY univention-ox-provisioning/requirements.txt /build/requirements/ox-provisioning.txt
RUN find /build/requirements/ -name '*.txt' -exec cat {} + \
  | egrep -v 'univention' \
  | grep -v 'six' \
  | sort \
  | uniq \
  > /build/requirements_all.txt \
 && rm -rf /build/requirements/

# package and Python dependency installation, base system configuration,
# and uninstallation - all in one step to keep image small
COPY alpine_apk_list.* /tmp/
RUN apk add --no-cache $(cat /tmp/alpine_apk_list.build) $(cat /tmp/alpine_apk_list.runtime) && \
	cp -v /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
	echo "Europe/Berlin" > /etc/timezone && \
	pip3 install --no-cache-dir --compile --upgrade pip && \
	pip3 install --no-cache-dir --compile --upgrade -r /build/requirements_all.txt && \
	apk del --no-cache $(cat /tmp/alpine_apk_list.build) && \
	python3 -c "from zeep import Client" && \
	rm -rf /tmp/*

COPY univention-ox-soap-api/ /tmp/univention-ox-soap-api/
RUN export OX_PROVISIONING_VERSION="$version" &&\
	pip3 install --no-cache-dir --compile --upgrade /tmp/univention-ox-soap-api && \
	python3 -c "from univention.ox.soap.services import get_ox_soap_service_class" && \
	python3 -c "from univention.ox.soap.backend_base import get_ox_integration_class" && \
	rm -rf /tmp/*

COPY univention-ox-provisioning /tmp/univention-ox-provisioning
COPY app/listener_trigger /tmp/app/
COPY tests /tmp/tests
COPY LICENSE /usr/local/share/ox-connector/LICENSE

# 1st linting, then installation
RUN apk add --no-cache gcc python3-dev musl-dev && \
	python3 -m venv --system-site-packages /tmp/venv && \
	. /tmp/venv/bin/activate && \
	pip3 install --no-cache-dir --compile -U pip && \
	pip3 install --no-cache-dir --compile black flake8 isort && \
	cd /tmp && \
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

#
# comment below out for final image
#
RUN apk add --no-cache vim

RUN apk add --no-cache py3-multidict py3-yarl && \
	pip3 install --no-cache-dir --compile udm-rest-client && \
	pip3 install --no-cache-dir --compile --index-url https://test.pypi.org/simple/ openapi-client-udm-ox && \
	python3 -c "from udm_rest_client.udm import UDM" && \
	python3 -c "import openapi_client_udm; openapi_client_udm.OxmailOxcontext.dn"

COPY univention-ox-provisioning/requirements_tests.txt tests/ /oxp/tests/
RUN pip3 install --no-cache-dir --compile --upgrade -r /oxp/tests/requirements_tests.txt && \
	python3 -m pytest --collect-only /oxp/tests && \
	rm -rf /oxp/.pytest_cache /oxp/tests/requirements_tests.txt
