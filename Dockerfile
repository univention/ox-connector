FROM python:3.8-alpine

RUN apk add libxml2-dev gcc libc-dev libxslt-dev
RUN pip install zeep

ADD python/*.py /usr/local/lib/python3.8/site-packages/oxconnector/

# for me. FIXME: remove
RUN apk add vim
RUN pip install pytest uritemplate
ADD test/*.py /usr/local/share/oxconnector/tests/
# super simple test that the very basics work
RUN python -c "import oxconnector.backend"

CMD [ "/sbin/init" ]
