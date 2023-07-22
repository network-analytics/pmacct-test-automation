## Test Description (104-IPFIXv10-IPv6-CISCO-sampling_option)

IPFIX v10 from CISCO ASR9k IOS XR with IPFIX Data Template 342 and option 257 (containing sampling information). This test's objective is verifying the nfacctd renormalization based on sampling option data.

### Provided files:

- traffic-00.pcap              pcap file (for traffic generator)
- traffic-reproducer-00.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip

- nfacctd-00.conf              nfacctd daemon configuration file
- librdkafka-00.conf           librdkafka configuration for nfacctd

- pretag-00.map                pretag mapping file for nfacctd              HINT: IPs need to match with repro_ips
- custom-primitives-00.lst     list of custom primitives for nfacctd

- output-flow-00.json          desired nfacctd kafka output [daisy.flow topic] containing json messages

### Test timeline:

pcap file time duration: 
t=0s --> the first full minute after starting the traffic generator

- t=2s:   IPFIX option-template and option packets sent
- t=7s:   IPFIX data-template and data packets sent

### Test execution and results:

Start traffic reproducer with provided config. When finished producing messages, the traffic reproducer will exit automatically (keep_open=false). 
After nfacctd produced to kafka (t=60s), check the following:

- The nfacctd kafka output messages in topic daisy.flow need to match with the json messages in "output-flow-00.json".
- The timestamp values will change between runs, with the only exceptions being timestamp_start and timestamp_end, which come from IPFIX fields and will stay the same.
- Order of the json messages could change
- No ERROR or WARN/WARNING messages are present in the logfile