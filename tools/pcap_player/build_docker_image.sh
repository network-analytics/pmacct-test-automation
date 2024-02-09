#!/bin/bash

IMG=debian

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

<<<<<<< HEAD
echo "Building traffic reproducer docker images"
docker build -t traffic-reproducer:_build -f $SCRIPT_DIR/single/Dockerfile_$IMG $SCRIPT_DIR || exit $?
docker build -t traffic-reproducer-multi:_build -f $SCRIPT_DIR/multi/Dockerfile_$IMG $SCRIPT_DIR || exit $?
=======
echo "Building traffic reproducer docker image"
docker build -t traffic-reproducer-multi:local -f $SCRIPT_DIR/multi/Dockerfile_$IMG $SCRIPT_DIR || exit $?
>>>>>>> Cleaned up image build scripts and files for using only multi image
