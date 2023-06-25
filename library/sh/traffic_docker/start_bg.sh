#!/bin/sh

PCAP_MOUNT_DIR="$1"
ID="$2"
IP_ADDRESS="$3"


echo "Starting traffic container with mounted folder: $1, ID: $2 and IP: $3"
docker run -d -v ${PCAP_MOUNT_DIR}:/pcap \
          --network pmacct_test_network \
          --ip $IP_ADDRESS \
          --name traffic-reproducer-"$ID" \
          traffic-reproducer
