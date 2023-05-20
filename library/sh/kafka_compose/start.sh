#!/bin/sh

# find directory, where this script resides
#SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

# deploy network and containers (zookeeper, broker and schema-registry)
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" up -d
