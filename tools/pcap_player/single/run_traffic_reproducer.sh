#!/bin/bash
exec > /pcap/run_traffic_reproducer.log
exec 2>&1
echo "$( date ) Running traffic reproducer"
echo "$( date ) Running /pcap/traffic-reproducer.yml"
python3 main.py -t /pcap/traffic-reproducer.yml -v > /pcap/traffic-reproducer.log 2>&1
echo "$( date ) Process finished, exiting"
