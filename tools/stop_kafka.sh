#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

echo "Stopping Kafka docker compose..."
$SCRIPT_DIR/../library/sh/kafka_compose/stop.sh
echo "Kafka docker compose undeployed"

echo "Deleting network..."
$SCRIPT_DIR/../library/sh/test_network/delete.sh
echo "Network deleted"
