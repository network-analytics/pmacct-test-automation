## Test Description (101-NFv9-CISCO-T313-cust_primitives)

NetFlow v9 from CISCO ASR9k IOS XR with IPFIX data only (template 313).

### Provided files:

- 101_test.py                               pytest file defining test execution

- traffic-00.pcap                           pcap file (for traffic generator)
- traffic-reproducer-00.conf                traffic replay function config file

- nfacctd-00.conf                           nfacctd daemon configuration file

- pmacct_mount/custom-primitives-00.lst     list of custom primitives for nfacctd

- output-flow-00.json                       desired nfacctd kafka output [daisy.flow topic] containing json messages
- output-log-00.log                         log messages that need to be in the logfile

### Test timeline:

t=0s --> the first full minute after starting the traffic generator

- t=1s:    IPFIX Data-Template packets sent
- t=6-7s:  IPFIX Data packets sent
- t=60s:   nfacctd producing flow data to kafka

### Test execution and results:

Start traffic reproducer with provided config. When finished producing messages, the traffic reproducer will exit automatically (keep_open=false). 
After nfacctd produced to kafka (t=60s), check the following:

- The nfacctd kafka output messages in topic daisy.flow need to match with the json messages in "output-flow-00.json".
- The timestamp values will change between runs (since we have NFv9 in this test, timestamp_start and timestamp_end also change between runs).
- Order of the json messages could change
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- No ERROR or WARN/WARNING messages are present in the logfile
