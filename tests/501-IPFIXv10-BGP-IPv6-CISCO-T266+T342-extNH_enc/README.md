## Test Description (501-IPFIXv10-BGP-IPv6-CISCO-T266+T342-extNH_enc)

IPFIX and BGP from IOS XR 7.8.2 with IPv6 transport. BGP with ext-NH encoding (ipv6 NH for ipv4 NLRI). Templates 266 and 342.

- MPLS VPN RD from option 334
- Sampling info from option 257
- IF_Name from option 256

### Provided files:

- 501_test.py                               pytest file defining test execution

- traffic-00.pcap                           pcap file (for traffic generator)
- traffic-reproducer-00.conf                traffic replay function config file

- nfacctd-00.conf                           nfacctd daemon configuration file

- pmacct_mount/pretag-00.map                pretag mapping file for nfacctd              HINT: IPs need to match with repro_ips
- pmacct_mount/custom-primitives-00.lst     list of custom primitives for nfacctd

- output-flow-00.json                       desired nfacctd kafka output [daisy.flow topic] containing json messages
- output-bgp-00.json                        desired nfacctd kafka output [daisy.bgp topic] containing json messages
- output-log-00.log                         log messages that need to be in the logfile

### Test timeline:

t=0s --> the first full minute after starting the traffic generator

- t=0s: BGP OPEN sent
- t=2-3s: BGP updates sent
- t=4-3s: IPFIX templates (option+data) sent 
- t=4-5s: IPFIX option-data sent
- t=9-10s: IPFIX data sent 
- t=60s:  nfacctd producing flow data to kafka

### Test execution and results:

Start traffic reproducer with provided config. When finished producing messages, the traffic reproducer will exit automatically (keep_open=false). 
After nfacctd produced to kafka (t=60s), check the following:

- The nfacctd kafka output messages in topic daisy.flow need to match with the json messages in "output-flow-00.json".
- The nfacctd kafka output messages in topic daisy.bgp need to match with  the json messages in "output-bgp-00.json".
- The timestamp values will change between runs, with the only exceptions being timestamp_start and timestamp_end, which come from IPFIX fields and will stay the same.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- Excluding the ones present in the output-log-00.log file, no additional ERROR or WARN/WARNING messages are present in the logfile
