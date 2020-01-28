FROM python:3.8-alpine

RUN apk add libxml2-dev gcc libc-dev libxslt-dev
RUN pip install zeep

# for me. FIXME: remove
RUN apk add vim

ADD python/*.py /usr/local/lib/python3.8/site-packages/oxconnector/
RUN python -c "import oxconnector.backend"
CMD [ "/sbin/init" ]
