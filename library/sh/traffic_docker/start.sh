#!/bin/sh

PCAP_MOUNT_DIR="$1"
IP_ADDRESS="$2"
IPv6_ADDRESS="$3"

IPV6STR=""
if [ -n "$IPv6_ADDRESS" ]; then
  IPV6STR="--ip6 $IPv6_ADDRESS"
fi

# Runs a traffic reproducer container synchronously

if docker inspect traffic-reproducer-0 >/dev/null 2>&1; then
    echo "Container exists, removing it"
    docker rm traffic-reproducer-0
fi

echo "Starting traffic container with mounted folder: $1"
docker run -v ${PCAP_MOUNT_DIR}:/pcap \
          --network pmacct_test_network \
          --ip $IP_ADDRESS $IPV6STR \
          --name traffic-reproducer-0 \
          traffic-reproducer

#--ip6 $IPv6_ADDRESS \