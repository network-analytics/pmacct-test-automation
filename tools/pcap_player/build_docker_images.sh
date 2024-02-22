#!/bin/bash

IMG=debian

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

echo "Building traffic reproducer docker images"
docker build -t traffic-reproducer:_build -f $SCRIPT_DIR/single/Dockerfile_$IMG $SCRIPT_DIR || exit $?
docker build -t traffic-reproducer-multi:_build -f $SCRIPT_DIR/multi/Dockerfile_$IMG $SCRIPT_DIR || exit $?
