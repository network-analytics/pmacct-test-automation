#!/bin/sh

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

echo "Installing needed apk packages"
apt -y install python3 || exit $?
apt -y install python3-pip || exit $?
apt -y install python3-dev || exit $?
apt -y install make || exit $?
apt -y install gcc || exit $?
apt -y install bash || exit $?
#apt install alpine-sdk || exit $?
apt -y install librdkafka-dev || exit $?

echo "Installing python library requirements"
pip install -r requirements.txt || exit $?

echo "Pulling docker images from repository"
cat settings.conf | awk -F '=' '{print $2}' | while read -r value; do
  if [ ! -z $value ]; then
    docker pull "$value"
  fi
done

echo "Building traffic reproducer docker images"
cd tools/pcap_player
docker build -t traffic-reproducer -f single/Dockerfile_debian . || exit $?
docker build -t traffic-reproducer-multi -f multi/Dockerfile_debian . || exit $?
