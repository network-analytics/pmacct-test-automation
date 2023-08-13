#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
  echo "No argument supplied"
  exit 1
fi
if [ $# -ne 2 ]; then
  echo "Two arguments expected: pcap folder (absolute path) and pcap player IP address"
  exit 1
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

echo "Starting pcap player"
$SCRIPT_DIR/../library/sh/traffic_docker/start.sh $1 $2 || exit $?
echo "Traffic replayed"
