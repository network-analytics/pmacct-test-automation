#!/bin/sh

echo "Running traffic reproducer multi"
#python3 main.py -t /pcap/traffic-reproducer.yml
ls /pcap/*/traffic-reproducer.yml | xargs -I {} sh -c 'sleep 1; python3 main.py -t {} &'
sleep 600
