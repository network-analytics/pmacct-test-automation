#!/bin/sh

# find directory, where this script resides
SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

# undeploy containers (zookeeper, broker and schema-registry)
docker compose --env-file $SCRIPT_DIR/../../../settings.conf -f "$SCRIPT_DIR/docker-compose.yml" down
