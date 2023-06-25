#!/bin/sh

hostip=$( hostname -i )
echo "Found host IP: $hostip"

#echo "Printing traffic-reproducer.conf"
#cat /pcap/traffic-reproducer.conf

sed -i "s/REPRO_IP_VALUE/${hostip}/g" /pcap/traffic-reproducer.conf
echo "Replaced REPRO_IP_VALUE in traffic-reproducer.conf"




echo "Running traffic reproducer"
python3 main.py -t /pcap/traffic-reproducer.conf

