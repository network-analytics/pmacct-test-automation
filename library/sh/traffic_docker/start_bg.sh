#!/bin/sh

PCAP_MOUNT_DIR="$1"
ID="$2"
IP_ADDRESS="$3"
IPv6_ADDRESS="$4"

IPV6STR=""
if [ -n "$IPv6_ADDRESS" ]; then
  IPV6STR="--ip6 $IPv6_ADDRESS"
fi

echo "Starting traffic container with mounted folder: $1, ID: $2 and IP: $3"
docker run -d -v ${PCAP_MOUNT_DIR}:/pcap \
          --network pmacct_test_network \
          --ip $IP_ADDRESS $IPV6STR \
          --name traffic-reproducer-"$ID" \
          traffic-reproducer
