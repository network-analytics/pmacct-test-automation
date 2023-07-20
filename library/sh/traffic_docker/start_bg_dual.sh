#!/bin/sh

PCAP_MOUNT_DIR1="$1"
PCAP_MOUNT_DIR2="$2"
ID="$3"
IP_ADDRESS="$4"
IPv6_ADDRESS="$5"

IPV6STR=""
if [ -n "$IPv6_ADDRESS" ]; then
  IPV6STR="--ip6 $IPv6_ADDRESS"
fi

echo "Starting traffic container with mounted folders: $PCAP_MOUNT_DIR1 and $PCAP_MOUNT_DIR2, ID: $3 and IP: $4"
docker run -d -v ${PCAP_MOUNT_DIR1}:/pcap1 -v ${PCAP_MOUNT_DIR2}:/pcap2 \
          --network pmacct_test_network \
          --ip $IP_ADDRESS $IPV6STR \
          --name traffic-reproducer-"$ID" \
          traffic-reproducer
