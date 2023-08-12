#!/bin/sh

# docker inspect will return 1 if redis container already exists
# if so, the redis container is removed (before it is deployed next)
docker inspect --format="{{ .State.Running }}" redis >/dev/null 2>&1
if [ $? -ne 1 ]; then
  docker rm redis
fi

# find directory, where this script resides, and load docker image URLs (REDIS_IMG is defined therein)
SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
source $SCRIPT_DIR/../../../settings.conf

# deploy Redis container
docker run --network pmacct_test_network \
           --ip 172.21.1.14 \
           --ip6 fd25::14 \
           --name redis \
           $REDIS_IMG >/dev/null 2>&1 &
