## Test Description (111-IPFIXv10-NFv9-IPv6-IPv4-mix_sources)

Test with IPFIX and NFv9 from 2 different source IPs, one ipv4 and the other ipv6, sending data to the same nfacctd daemon.

### Provided files:

- 111_test.py                               pytest file defining test execution

- traffic-00.pcap                           pcap file (for traffic generator)
- traffic-01.pcap                           pcap file (for traffic generator)
- traffic-reproducer-00.conf                traffic replay function config file      
- traffic-reproducer-01.conf                traffic replay function config file

- nfacctd-00.conf                           nfacctd daemon configuration file

- pmacct_mount/pretag-00.map                pretag mapping file for nfacctd              HINT: IPs need to match with repro_ips
- pmacct_mount/custom-primitives-00.lst     list of custom primitives for nfacctd

- output-flow-00.json                       desired nfacctd kafka output [daisy.flow topic] containing json messages
- output-log-00.log                         log messages that need to be in the logfile

### Test timeline:
t=0s --> the first full minute after starting the traffic generator

pcap traffic-00.pcap file time duration: 
- t=1s: NFv9 templates sent  
- t=6s: NFv9 data sent 

pcap traffic-01.pcap file time duration: 
- t=5s: IPFIXv10 templates sent
- t=7s: IPFIXv10 data sent 

### Test execution and results:

Start the 2 traffic reproducers with provided configs. When finished producing messages, the traffic reproducer will exit automatically (keep_open=false). 
After nfacctd produced to kafka (t=60s), check the following:

- The nfacctd kafka output messages in topic daisy.flow need to match with the json messages in "output-flow-00.json".
- The timestamp values will change between runs (since we have NFv9 in this test, timestamp_start and timestamp_end also change between runs).
- Order of the json messages could change
- No ERROR or WARN/WARNING messages are present in the logfile
