#!/bin/bash

if [ -z "$1" ]; then
  echo "No argument supplied, assuming alpine as base image"
  IMG="alpine"
elif [[ $1 != "alpine" && $1 != "debian" ]]; then
  echo "Invalid base image, only alpine and debian are available"
  exit 1
else
  IMG="$1"
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

echo "Building traffic reproducer docker images"
docker build -t traffic-reproducer -f $SCRIPT_DIR/single/Dockerfile_$IMG $SCRIPT_DIR || exit $?
docker build -t traffic-reproducer-multi -f $SCRIPT_DIR/multi/Dockerfile_$IMG $SCRIPT_DIR || exit $?
