## Test Description (202-BMP-pmbmpd-CISCO-HUAWEI-multiple-sources)

IMPORTANT: for this test we use the pmbmpd daemon (not nfacctd)!

Testing with BMP traffic from 3 different source IPs.

### Provided files:

- traffic-00.pcap              pcap file 1 (for traffic generator)
- traffic-01.pcap              pcap file 2 (for traffic generator)
- traffic-02.pcap              pcap file 3 (for traffic generator)
- traffic-reproducer-00.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip
- traffic-reproducer-01.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip
- traffic-reproducer-02.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip

- pmbmpd-00.conf               pmbmpd daemon configuration file
- librdkafka-00.conf           librdkafka configuration for pmbmpd

- pretag-00.map                pretag mapping file for pmbmpd              HINT: IPs need to match with repro_ips

- output-bmp-00.json           desired pmbmpd kafka output [daisy.bgp topic] containing json messages [before closing sockets]
- output-log-00.log            log messages that need to be in the logfile [before closing sockets]          HINT: contains variable parameters
- output-log-01.log            log messages that need to be in the logfile [after closing socket]            HINT: contains variable parameters

### Test timeline:

t=0s --> the first full minute after starting the traffic generator

pcaps file time duration: 
- t=1-3s: BMP packets sent (from all 4 reproducers)

### Test execution and results:

1. Part 1: start traffic reproducers (00, 01, 02) with provided configs. 

IMPORTANT: do not kill the traffic reproducer processes!

After reproducing all the packet, the traffic generators do not exit (thanks to keep_open: true), and thus the TCP sockets with nfacctd thus remain open. Check the following:

- The pmbmpd kafka output messages in topic daisy.bmp need to match with the json messages in "output-bmp-00.json".
- The timestamp values will change between runs.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- HINT: ${repro_ip} can be one of the 3 repro-ips used by the reproducers!
- Excluding the ones present in the output-log-00.log file, no additional ERROR or WARN/WARNING messages are present in the logfile

2. Part 2: 

Now kill the traffic reproducer (e.g. with CTRL-C). This will close the TCP sockets with nfacctd. 
Then check the following:

- Log messages in "output-log-01.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- Excluding the ones present in the output-log-01.log file, no additional ERROR or WARN/WARNING messages are present in the logfile