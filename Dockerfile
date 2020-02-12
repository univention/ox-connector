FROM alpine:3.11

ARG version

WORKDIR /oxp

CMD ["/sbin/init"]

LABEL "description"="UCS OX provisioning app" \
    "version"="$version"

# package and Python dependency installation, base system configuration,
# and uninstallation - all in one step to keep image small
COPY alpine_apk_list.* requirements_all.txt /tmp/
RUN apk add --no-cache $(cat /tmp/alpine_apk_list.build) $(cat /tmp/alpine_apk_list.runtime) && \
	cp -v /usr/share/zoneinfo/Europe/Berlin /etc/localtime && \
	echo "Europe/Berlin" > /etc/timezone && \
	pip3 install --no-cache-dir --compile --upgrade pip && \
	pip3 install --no-cache-dir --compile --upgrade -r /tmp/requirements_all.txt && \
	apk del --no-cache $(cat /tmp/alpine_apk_list.build) && \
	python3 -c "from zeep import Client" && \
	rm -rf /tmp/*

COPY appsuite/univention-ox/ /tmp/univention-ox/
RUN pip3 install --no-cache-dir --compile --upgrade /tmp/univention-ox && \
	python3 -c "from univention.ox.backend_base import get_ox_integration_class" && \
	rm -rf /tmp/*

COPY appsuite/univention-ox-soap-api/ /tmp/univention-ox-soap-api/
RUN pip3 install --no-cache-dir --compile --upgrade /tmp/univention-ox-soap-api && \
	python3 -c "from univention.ox.soap.services import get_ox_soap_service_class" && \
	rm -rf /tmp/*

COPY univention-ox-provisioning /tmp/univention-ox-provisioning
# 1st linting, then installation
RUN apk add --no-cache gcc python3-dev musl-dev && \
	python3 -m venv /tmp/venv && \
	pip3 install --no-cache-dir --compile black flake8 isort pip && \
	cd /tmp/univention-ox-provisioning && \
	make lint && \
	pip3 install --no-cache-dir --compile /tmp/univention-ox-provisioning && \
	/usr/bin/python3 -c "from univention.ox.provisioning.listener_trigger import load_from_json_file" && \
	apk del --no-cache gcc python3-dev musl-dev && \
	rm -rf /tmp/*

COPY appsuite/univention-ox/share/ /usr/local/share/ox-connector/resources
COPY appsuite/univention-ox/udm/ /usr/local/share/ox-connector/resources/udm
COPY appsuite/univention-ox/umc/ /usr/local/share/ox-connector/resources/umc
COPY appsuite/univention-ox/ldap/ /usr/local/share/ox-connector/resources/ldap

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
