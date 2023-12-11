#!/bin/bash

# exit if bad arguments
if [ -z "$1" ]; then
    echo "No docker-compose file supplied"
    exit 1
fi
DOCKER_COMPOSE_FILE="$1"
DETACHED="$2"
docker-compose -f $DOCKER_COMPOSE_FILE up $DETACHED

