#!/bin/sh

# docker inspect will return 1 if pmacct container already exists
# if so, the pmacct container is removed (before it is deployed next)
docker inspect --format="{{ .State.Running }}" redis >/dev/null 2>&1
if [ $? -ne 1 ]; then
  docker rm redis
fi

# deploy pmacct container
docker run --ip 172.111.1.14 \
           --ip6 fd25::14 \
           --name redis \
           redis >/dev/null 2>&1 &
