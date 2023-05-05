#!/bin/sh

PMACCT_CONF="$1"

PMACCT_MOUNT="$2"

# find directory, where this script resides
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# docker inspect will return 1 if pmacct container already exists
# if so, the pmacct container is removed (before it is deployed next)
docker inspect --format="{{ .State.Running }}" pmacct >/dev/null 2>&1
if [ $? -ne 1 ]; then
  docker rm pmacct
fi

# deploy pmacct container
docker run -v "$PMACCT_CONF":/etc/pmacct/nfacctd.conf \
           -v "$PMACCT_MOUNT":/var/log/pmacct \
           --network pmacct_test_network \
           -p 2929:8989/udp \
           --name pmacct \
           remote-docker.artifactory.swisscom.com/pmacct/nfacctd >/dev/null 2>&1 &

