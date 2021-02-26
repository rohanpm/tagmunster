FROM alpine:3.13

RUN apk add -U python3 py3-requests py3-pip py3-attrs py3-wrapt py3-jsonschema py3-virtualenv git
# RUN pip install pidiff

COPY src /tagmunster-src
RUN pip install --editable /tagmunster-src

COPY src/tagmunster-test /usr/local/bin/tagmunster-test

ENTRYPOINT ["/usr/bin/tagmunster"]
