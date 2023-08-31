#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

echo "Building traffic reproducer docker images"
docker build -t traffic-reproducer -f $SCRIPT_DIR/single/Dockerfile_debian $SCRIPT_DIR || exit $?
docker build -t traffic-reproducer-multi -f $SCRIPT_DIR/multi/Dockerfile_debian $SCRIPT_DIR || exit $?
