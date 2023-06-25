#!/bin/sh

PCAP_MOUNT_DIR="$1"
IP_ADDRESS="$2"

# Runs a traffic reproducer container synchronously

echo "Starting traffic container with mounted folder: $1"
docker run -v ${PCAP_MOUNT_DIR}:/pcap \
          --network pmacct_test_network \
          --ip $IP_ADDRESS \
          --name traffic-reproducer-0 \
          traffic-reproducer
