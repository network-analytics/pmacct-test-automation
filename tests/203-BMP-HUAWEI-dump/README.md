## Test Description(203-BMP-HUAWEI-dump)

Test for verifying BMP regular dump feature. Pcap taken from test 200: Huawei VRP 8.210 (daisy-61 IETF lab) [with global and loc rib instance peers].

### Provided files:

- traffic-00.pcap              pcap file (for traffic generator)
- traffic-reproducer-00.conf   traffic replay function config file          HINT: you'll have to adjust repro_ip

- nfacctd-00.conf              nfacctd daemon configuration file
- librdkafka-00.conf           librdkafka configuration for nfacctd

- output-bmp-00.json           desired nfacctd kafka output [daisy.bgp topic] containing json messages
- output-bmp-dump-00.json           desired nfacctd kafka output [daisy.bgp topic] containing json messages
- output-log-00.log            log messages that need to be in the logfile                                  HINT: contains variable parameters
- output-log-01.log            log messages that need to be in the logfile                                  HINT: contains variable parameters

### Test timeline:

pcap file time duration: 
t=0s --> the first full minute after starting the traffic generator

- t=5s: BMP packets sent 

### Test execution and results:

Part 1: Start traffic reproducer with provided config. 

IMPORTANT: do not kill the traffic reproducer process!

After reproducing all the packet, the traffic generator does not exit (thanks to keep_open: true in traffic-reproducer-00.conf), and thus the TCP sockets with nfacctd thus remain open. 
Check the following:

- The nfacctd kafka output messages in topic daisy.bmp need to match with  the json messages in "output-bmp-00.json".
- The timestamp values will change between runs.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)
- Log messages in "output-log-00.log" are present in the logfile (order of appearence preserved, but there could/will be other logs in between)
- Excluding the ones present in the output-log-00.log file, no additional ERROR or WARN/WARNING messages are present in the logfile

Part 2: Now wait until the next BMP dump happens (configured every 2mins). The dump event can be detected by looking for the log message in output-log-01.log

Then check the following: 

- The nfacctd kafka output messages in topic daisy.bmp.dump need to match with  the json messages in "output-bmp-dump-00.json".
- The timestamp values will change between runs.
- Order of the json messages could change (this means you also have to ignore any sequence numbers when comparing the json output!)