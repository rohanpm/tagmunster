FROM alpine:3.13

# RUN apk update
RUN apk add -U python3 py3-requests git

COPY tagmunster /usr/local/bin/tagmunster
COPY tagmunster-test /usr/local/bin/tagmunster-test

ENTRYPOINT ["/usr/local/bin/tagmunster"]
