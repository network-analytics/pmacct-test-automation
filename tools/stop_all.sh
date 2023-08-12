#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

tools/stop_pmacct.sh
tools/stop_kafka.sh
tools/stop_redis.sh