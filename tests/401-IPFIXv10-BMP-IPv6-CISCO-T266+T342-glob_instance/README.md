## Test Description (401-IPFIXv10-BMP-IPv6-CISCO-T266+T342-glob_instance)

IPFIX v10 + BMP global instance with IPV6 transport from CISCO IOS XR 7.8.2. Data-templates 266 and 342. Options Templates 334, 338, 256, 257.

### Provided files:

- 401_test.py                               pytest file defining test execution

- traffic-00.pcap                           pcap file (for traffic generator)
- traffic-reproducer-00.yml                 traffic replay function config file

- nfacctd-00.conf                           nfacctd daemon configuration file

- pmacct_mount/pretag-00.map                pretag mapping file for nfacctd              HINT: IPs need to match with repro_ips
- pmacct_mount/custom-primitives-00.lst     list of custom primitives for nfacctd

- output-flow-00.json                       desired nfacctd kafka output [daisy.flow topic] containing json messages
- output-bmp-00.json                        desired nfacctd kafka output [daisy.bmp topic] containing json messages
- output-log-00.log                         log messages that need to be in the logfile

### Test timeline:

t=0s --> the first full minute after starting the traffic generator

- t=1s: BMP Open
- t=3s: BMP Updates
- t=4s: IPFIX options templates + option data
- t=5s: IPFIX templates
- t=7s-8s: IPFIX data

### Test execution and results:

Start traffic reproducer with provided config. When finished producing messages, the traffic reproducer will exit automatically (keep_open=false). 
After nfacctd produced to kafka (t=60s), check the following:

- The nfacctd kafka output messages in topic daisy.flow need to match with the json messages in "output-flow-00.json".
- The nfacctd kafka output messages in topic daisy.bmp need to match with  the json messages in "output-bmp-00.json".
- The timestamp values will change between runs, with the only exceptions being timestamp_start and timestamp_end, which come from IPFIX fields and will stay the same.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- Excluding the ones present in the output-log-00.log file, no additional ERROR or WARN messages are present in the logfile
