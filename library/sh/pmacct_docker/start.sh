#!/bin/sh

PMACCT_CONF="$1"
PMACCT_MOUNT="$2"
PMACCT_DAEMON="$3"

DOCKER_IMAGE="pmacct/${PMACCT_DAEMON}:bleeding-edge"
if [[ "$PMACCT_DAEMON" == "nfacctd" ]]; then
  DOCKER_IMAGE="remote-docker.artifactory.swisscom.com/${DOCKER_IMAGE}"
fi

# docker inspect will return 1 if pmacct container already exists
# if so, the pmacct container is removed (before it is deployed next)
docker inspect --format="{{ .State.Running }}" pmacct >/dev/null 2>&1
if [ $? -ne 1 ]; then
  docker rm pmacct
fi

echo "Docker image: $DOCKER_IMAGE"

# deploy pmacct container
docker run -v "$PMACCT_CONF":/etc/pmacct/${PMACCT_DAEMON}.conf \
           -v "$PMACCT_MOUNT":/var/log/pmacct \
           --network pmacct_test_network \
           --ip 172.111.1.13 \
           --ip6 fd25::13 \
           --name pmacct \
           $DOCKER_IMAGE >/dev/null 2>&1 &

           # remote-docker.artifactory.swisscom.com/pmacct/nfacctd:bleeding-edge >/dev/null 2>&1 &

           # port publishing not needed anymore, since traffic reproducers are running in a container in the
           # same network now
           #-p 2929:8989/udp \
           #-p 2929:8989/tcp \
           #--name pmacct \
           #remote-docker.artifactory.swisscom.com/pmacct/nfacctd:bleeding-edge >/dev/null 2>&1 &
