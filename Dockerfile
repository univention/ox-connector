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
RUN pip3 install --no-cache-dir --compile /tmp/univention-ox-provisioning && \
	python3 -c "from univention.ox.provisioning.listener_trigger import load_from_json_file" && \
	rm -rf /tmp/*

COPY resources /usr/local/share/ox-connector/resources

#
# comment below out for final image
#
RUN apk add --no-cache vim

COPY univention-ox-provisioning/requirements_tests.txt tests/ /oxp/tests/
RUN pip3 install --no-cache-dir --compile --upgrade -r /oxp/tests/requirements_tests.txt && \
	python3 -m pytest --collect-only /oxp/tests && \
	rm -f /oxp/tests/requirements_tests.txt
