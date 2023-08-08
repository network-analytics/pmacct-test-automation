#!/bin/sh

PMACCT_CONF="$1"
PMACCT_MOUNT="$2"
PMACCT_DAEMON="$3"
PMACCT_IMAGE="$4"

# docker inspect will return 1 if pmacct container already exists
# if so, the pmacct container is removed (before it is deployed next)
docker inspect --format="{{ .State.Running }}" pmacct >/dev/null 2>&1
if [ $? -ne 1 ]; then
  docker rm pmacct
fi

# deploy pmacct container
docker run -v "$PMACCT_CONF":/etc/pmacct/${PMACCT_DAEMON}.conf \
           -v "$PMACCT_MOUNT":/var/log/pmacct \
           --network pmacct_test_network \
           --ip 172.111.1.13 \
           --ip6 fd25::13 \
           --name pmacct \
           $PMACCT_IMAGE >/dev/null 2>&1 &
