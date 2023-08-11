#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

echo "Stopping pmacct docker container..."
$SCRIPT_DIR/../library/sh/pmacct_docker/stop.sh
echo "Pmacct docker container undeployed"
