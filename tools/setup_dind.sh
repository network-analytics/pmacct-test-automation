#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

echo "Installing needed apk packages"
apk add python3 || exit $?
apk add py3-pip || exit $?
apk add python3-dev || exit $?
apk add make || exit $?
apk add gcc || exit $?
apk add bash || exit $?
apk add alpine-sdk || exit $?
apk add librdkafka-dev || exit $?

echo "Installing python library requirements"
pip install -r requirements.txt || exit $?

echo "Pulling docker images from repository"
cat settings.conf | grep -Po "(?<==).+" | xargs docker pull

echo "Building traffic reproducer docker images"
cd tools/pcap_player
docker build -t traffic-reproducer -f single/Dockerfile . || exit $?
docker build -t traffic-reproducer-multi -f multi/Dockerfile . || exit $?
