## Test Description(200-BMP-HUAWEI-locrib_instance)

BMP test with pcap from Huawei VRP 8.210 (daisy-61 IETF lab) [with global and loc rib instance peers].

### Provided files:

- traffic-00.pcap              pcap file (for traffic generator)
- traffic-reproducer-00.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip

- nfacctd-00.conf              nfacctd daemon configuration file
- librdkafka-00.conf           librdkafka configuration for nfacctd

- pretag-00.map                pretag mapping file for nfacctd              HINT: IPs need to match with repro_ips

- output-bmp-00.json           desired nfacctd kafka output [daisy.bgp topic] containing json messages
- output-log-00.log            log messages that need to be in the logfile                                  HINT: contains variable parameters

### Test timeline:

pcap file time duration: 
t=0s --> the first full minute after starting the traffic generator

- t=5s: BMP packets sent 

### Test execution and results:

Start traffic reproducer with provided config. When finished producing messages, the traffic reproducer will exit automatically (keep_open=false). 
After nfacctd produced to kafka, check the following:

- The nfacctd kafka output messages in topic daisy.bmp need to match with  the json messages in "output-bmp-00.json".
- The timestamp values will change between runs.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- Excluding the ones present in the output-log-00.log file, no additional ERROR or WARN/WARNING messages are present in the logfile
