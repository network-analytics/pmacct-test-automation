## Test Description (100-IPFIXv10-CISCO-T260+T261)

IPFIX v10 from CISCO ASR9k IOS XR 7.5.2 with IPFIX data only (templates 260 and 261).

### Provided files:

- traffic-00.pcap              pcap file (for traffic generator)
- traffic-reproducer-00.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip

- nfacctd-00.conf              nfacctd daemon configuration file
- librdkafka-00.conf           librdkafka configuration for nfacctd

- output-flow-00.json          desired nfacctd kafka output [daisy.flow topic] containing json messages

### Test timeline:

pcap file time duration: ~20s
t=0s --> the first full minute after starting the traffic generator

- t=0s:   IPFIX Data-Template packets sent
- t=20s:  IPFIX Data packets sent
- t=60s:  nfacctd producing flow data to kafka

### Test execution and results:

Start traffic reproducer with provided config. When finished producing messages, the traffic reproducer will exit automatically (keep_open=false). 
After nfacctd produced to kafka (t=60s), check the following:

- The nfacctd kafka output messages in topic daisy.flow need to match with the json messages in "output-flow-00.json". 
- The timestamp values will change between runs, with the only exceptions being timestamp_start and timestamp_end, which come from IPFIX fields and will stay the same.
- Order of the json messages could change
- No ERROR or WARN/WARNING messages are present in the logfile