## Test Description (302-BGP-IPv6-multiple-sources)

Testing with BGP traffic from 4 senders (mix ipv4 and ipv6), with 3 different source IPs. 2 senders have same IP and send the same BGP packets: pmacct will refuse the second connection. Testing also pretag with mix ipv4 and ipv6.

### Provided files:

- traffic-01.pcap              pcap file (for traffic reproducer)
- traffic-02.pcap              pcap file (for traffic reproducer)
- traffic-02.pcap              pcap file (for traffic reproducer)
- traffic-03.pcap              pcap file (for traffic reproducer)
- traffic-reproducer-00.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip
- traffic-reproducer-01.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip
- traffic-reproducer-02.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip
- traffic-reproducer-03.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip

- nfacctd-00.conf              nfacctd daemon configuration file
- librdkafka-00.conf           librdkafka configuration for nfacctd

- pretag-00.map                pretag mapping file for nfacctd              HINT: IPs need to match with repro_ips

- output-bgp-00.json           desired nfacctd kafka output [daisy.bgp topic] containing json messages
- output-log-00.log            log messages that need to be in the logfile                                  HINT: contains variable parameters

### Test timeline:

t=0s --> the first full minute after starting the traffic generator

pcaps file time duration: 
- t=1-2s: BGP packets sent (from reproducers 00-02)
- t=20-21s: BGP packets sent (from reproducer 03)

### Test execution and results:

1. Part 1: start traffic reproducers (00, 01, 02, 03) with provided configs. Make sure that you start the reproducers after 30s of a full minute, otherwise it could happen that reproducer 03 sends its packets before!

IMPORTANT: do not kill the traffic reproducer process of traffic-generator-02, which stays open thanks to keep_open=true!

Check the following at t=60s:

- The nfacctd kafka output messages in topic daisy.bgp need to match with  the json messages in "output-bgp-00.json".
- The timestamp values will change between runs, with the only exceptions being timestamp_start and timestamp_end, which come from IPFIX fields and will stay the same.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- HINT: ${repro_ip} and ${bgp_id} can be one of the 4 used by the reproducers!
- Excluding the ones present in the output-log-00.log file, no additional ERROR or WARN/WARNING messages are present in the logfile

2. Part 2: 

Now kill the traffic reproducer 02 (e.g. with CTRL-C). This will close the TCP sockets with nfacctd. 
Then check the following:

- Log messages in "output-log-01.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- Excluding the ones present in the output-log-01.log file, no additional ERROR or WARN/WARNING messages are present in the logfile