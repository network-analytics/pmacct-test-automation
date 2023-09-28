## Test Description (300-BGP-IPv6-CISCO-extNH_enc)

BGP from IOS XR 7.8.2 (ipt-zhh921-b-des-01) containing multi-protocol, route-refresh, 4-byte AS-number, and extended-next-hop-encoding capabilities.

### Provided files:

- 300_test.py                               pytest file defining test execution

- traffic-00.pcap                           pcap file (for traffic generator)
- traffic-reproducer-00.conf                traffic replay function config file

- nfacctd-00.conf                           nfacctd daemon configuration file

- pmacct_mount/pretag-00.map                pretag mapping file for nfacctd              HINT: IPs need to match with repro_ips

- output-bgp-00.json                        desired nfacctd kafka output [daisy.bgp topic] containing json messages
- output-log-00.log                         log messages that need to be in the logfile

### Test timeline:

t=0s --> the first full minute after starting the traffic generator

- t=27-28s: BGP OPEN sent
- t=31-33s: BGP updates sent

### Test execution and results:

1. Part 1: start traffic reproducer with provided config. 

IMPORTANT: do not kill the traffic reproducer process!

After reproducing all the packet, the traffic generator does not exit (thanks to keep_open: true in traffic-reproducer-00.conf), and thus the TCP sockets with nfacctd thus remain open. 
Check the following:

- The nfacctd kafka output messages in topic daisy.bgp need to match with  the json messages in "output-bgp-00.json".
- The timestamp values will change between runs.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- Excluding the ones present in the output-log-00.log file, no additional ERROR or WARN messages are present in the logfile

2. Part 2: 

Now kill the traffic reproducer (e.g. with CTRL-C). This will close the TCP sockets with nfacctd. Then check the following:
- Log messages in "output-log-01.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
