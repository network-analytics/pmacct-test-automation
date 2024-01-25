# Pmacct Test Automation Framework

This repo provides a testing framework based on pytest to perform regression testing on the [pmacct](https://github.com/pmacct/pmacct) project.

### Framework Architecture Overview

All the components (kafka stack, pmacct daemon, and traffic reproducer) are deployed as docker containers. Pytest orchestrates the setup, specific test configuration, execution, and verification logic.


<p align="center">
  <img src="docs/framework-architecture.png" alt="drawing" width="600"/>
</p>

**Supported pmacct daemons:**
- nfacctd
- pmbgpd
- pmbmpd
- *sfacctd* [**coming soon...**]
- *pmtelemetryd* [**coming soon...**]

**Network Telemetry Protocols currently included in the tests:**
- IPFIX / NFv9
- BMP
- BGP
- *YANG Push* [**coming soon...**]

## 1 - How To Install

Clone the repository (need to recurse to initialize and update submodules):
```shell
git clone https://github.com/network-analytics/pmacct-test-automation.git --recurse-submodules
```

Update the repository (need to recurse to update submodules):
```shell
git pull --recurse-submodules
```

Create and activate Python virtual envirinment:
```shell
python -m venv venv
source ./venv/bin/activate
```

Install/Update Python project dependencies:
```shell
pip install -r requirements.txt
```

Build single- and multi-pcap traffic reproducer images:
```shell
tools/pcap_player/build_docker_images.sh
```

Build pmacct images (checkout to desired branch or commit first):
```shell
tools/pmacct_build/build_docker_images.sh
```

## 2 - How To Run

To run one or more test cases:
```shell
./runtest.sh  [--dry] \
              [--loglevel=<log level>] \
              [--mark=<expression>] \
              [--key=<expression>] <test case number or wildcard>[:<scenario or wildcard>] \
              [<TC number or wildcard>[:<scenario or wildcard>] ... ]

Examples:
./runtest.sh 202                      run test 202 with default log level INFO              [all scenarios]
./runtest.sh 202:**                   run test 202 with default log level INFO              [all scenarios]
./runtest.sh 202:00                   run test 202 with default log level INFO              [default scenario]
./runtest.sh 103:02                   run test 202 with default log level INFO              [scenario 2]
./runtest.sh 101 102 201 301          run tests 101, 102, 201 and 301 with log level INFO   [all scenarios]
./runtest.sh 1*                       run all 1XX tests with log level INFO                 [all scenarios]
./runtest.sh 4*:01                    run all 4XX tests with log level INFO                 [scenarios 1]
./runtest.sh --loglevel=DEBUG 2*      run all 2XX test cases with log level DEBUG           [all scenarios]
./runtest.sh *                        run all test cases with log level INFO                [all scenarios]
./runtest.sh *:00                     run all test cases with log level INFO                [default scenarios only]
./runtest.sh --dry 4*                 dry-run all 4xx test cases                            [all scenarios]  
./runtest.sh --dry 401:01             dry-run test 401                                      [scenario 1]
```

Example (run test case 300 [default scenario] with python without the ./runtest.sh wrapper):
```shell
python3 -m pytest tests/300* --runconfig=300:00 --log-cli-level=DEBUG --log-file=results/pytestlog.log --html=results/report.html
```

In exceptional situations, e.g. when setup or teardown fails or is stopped, there may be some remaining components left running.
To stop Kafka components, including the created network, do:
```shell
tools/stop_all.sh
```

Local folder **results/\<test case\>/pmacct_mount** is mounted on pmacct container's folder **/var/log/pmacct**

Local folder(s) **results/\<test case\>/pcap_mount_n** are mounted on traffic reproducer container's folder **/pcap**

## 3 - Test Cases

### 1XX - IPFIX/NFv9/sFLOW
```
- 100: IPFIXv10-CISCO
- 101: NFv9-CISCO-cust_primitives
- 102: NFv9-CISCO-f2rd-pretag-sampling-reload
- 103: IPFIXv10-CISCO-JSON_encoding
- 104: IPFIXv10-IPv6-CISCO-sampling_option
- 110: IPFIXv10-NFv9-multiple-sources
- 111: IPFIXv10-NFv9-IPv6-IPv4-mix_sources
```

### 2XX - BMP
```
- 200: BMP-HUAWEI-locrib_instance
- 201: BMP-CISCO-rd_instance
- 202: BMP-CISCO-HUAWEI-multiple-sources
- 203: BMP-HUAWEI-dump
- 204: BMP-CISCO-peer_down
- 205: BMP-6wind-FRR-peer_down
```

### 3XX - BGP
```
- 300: BGP-IPv6-CISCO-extNH_enc
- 301: BGP-CISCO-pretag
- 302: BGP-IPv6-multiple-sources
```

### 4XX - IPFIX/NFv9 + BMP
```
- 400: IPFIXv10-BMP-CISCO-SRv6-multiple-sources
- 401: IPFIXv10-BMP-IPv6-CISCO-MPLS-multiple-sources
```

### 5XX - IPFIX/NFv9 + BGP
```
- 500: IPFIXv10-BGP-CISCO-SRv6
- 501: IPFIXv10-BGP-IPv6-CISCO-MPLS
- 502: IPFIXv10-BGP-IPv6-lcomms         [TODO: add]
```

### 9XX - Miscellaneous
```
- 900: kafka-connection-loss
- 901: redis-connection-loss
- 902: log-rotation-signal              [TODO: fix or move to dev branch]
```

## 4 - Developing Test Cases

In general, refer to the existing test cases as an example on how to develop additional ones.
Here are some useful guidelines to keep in mind when developing new test cases. 

For a new test it is necessary to provide at least the following files:
```
- XXX_test.py                             pytest file defining test execution

- traffic-00.pcap                         pcap file (for traffic generator)
- traffic-reproducer-00.yml               traffic replay function config file

- <pmacct-daemon>-00.conf                 daemon configuration file
- output-<type>-00.json                   desired nfacctd kafka (or log) output containing json messages (or patterns)
```

Other files can be added or might be necessary depending on the specific test.

### Pcap File

A pcap file containing the desired telemetry packets to be reproduced to the collector needs to be provided. 

The [Traffic Reproducer Project](https://github.com/network-analytics/traffic-reproducer) project provides a feature to pre-process a pcap, which can be used to clean up for example a tcpdump capture of telemetry data from lab router. This ensures that the Network Telemetry sessions within the pcap file are complete and well formed so that they can be deterministically reproduced at every test run. Refer to the [README](https://github.com/network-analytics/traffic-reproducer#pcap-pre-processing) and [examples](https://github.com/network-analytics/traffic-reproducer/tree/master/examples/pcap_processing) in the project for usage instructions.

### Expected json output

The framework can also be used to generate the expected json output files that pmacct produces to kafka. Just keep in mind that the json output needs to be manually checked to verify that the data received is as expected.

This is possible since the framework will always provide the kafka dumps (in the [results](results) folder) for each test after execution. The only problem is that without any output-XXX.json files, the tests will fail throwing a *file_not_found* error.

As example, if we want to generate the output files for test 100 (assuming that the output-flow-00.json file is not existing yet), we cannot just run the test normally as the *read_and_compare_messages* function will throw an error.
```
def main(consumer):
    assert scripts.replay_pcap(testParams.pcap_folders[0])

    assert test_tools.read_and_compare_messages(consumer, testParams, 'flow-00',
        ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])
```

To overcome this, we can temporarily replace that function with another one specifically developed for this purpose:
```
    assert test_tools.read_messages_dump_only(consumer, testParams, 'flow-00', wait_time=120)             # wait_time is optional (default=120s)
```

It's also possible to keep all the original arguments and just replace the function name, as the ignore_fields parameter will simply be ignored:
```
    assert test_tools.read_messages_dump_only(consumer, testParams, 'flow-00',
        ['stamp_inserted', 'stamp_updated', 'timestamp_max', 'timestamp_arrival', 'timestamp_min'])       # wait_time is optional (default=120s)
```

This way we can simply call:
```
./runtest 100
```
and the test will be executed omitting the output check, just consuming and dumping all messages sent to the kafka topic for the specified wait_time.

The json data can be found in the [results/100-IPFIXv10-CISCO/kafka_dumps](results/100-IPFIXv10-CISCO/kafka_dumps) folder and its content can be used to generate the output-flow-00.json file. 

### Expected log output

The framework allows for checking the logfile as well, i.e. to detect if any ERROR or WARNING messages are present or to look for specific log lines or patterns. Have a look at tests 102, 103, 203, 400, 500 for some examples.

Concretely, this works by adding in the test file something like:
```
    # Match for patterns in a provided file
    logfile = testParams.log_files.getFileLike('log-00')
    test_tools.transform_log_file(logfile)
    assert helpers.check_file_regex_sequence_in_file(testParams.pmacct_log_file, logfile)

    # Match for patterns provided directly
    assert not helpers.check_regex_sequence_in_file(testParams.pmacct_log_file, ['ERROR|WARN'])
```

The framework provides a helper function (*test_tools.transform_log_file*), which transforms some specific macros in regular expressions that can be directly matched with the live pmacct log output.

As an example, the following line:
```
${TIMESTAMP} INFO ( nfacctd_core/core/BMP ): [${repro_ip}] BMP peers usage: 1/600
```

will be transformed to:
```
\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z INFO \( nfacctd_core/core/BMP \): \[172\.21\.1\.101] BMP peers usage: 1/600
```

**List of currently supported macros:**
```
**MACRO**        **REGEX**                                         **EXAMPLE MATCH**            **COMMENTS**
TIMESTAMP        \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z              2024-01-22T14:36:04Z
IGNORE_REST      \.                                                (anything)                   Can only be used to ignore anything at the end of the string
RANDOM           .+                                                (anything)
retro_ip         172\.21\.1\.101                                   172.21.1.101                 Taken from traffic-reproducer-XX.yml
```

### Scenarios

Some tests such as 103 have different scenarios, i.e. multiple execution of the same test logic (pytest file and pcap file do not change), but with different pmacct configuration and possibly different expected output file.

To add different scenarios for an existing test, it's enough to create a subfolder **scenario-XX** where XX=scenario number. Then in this subfolder just place all the files (config, expected output) that need to be changed for the scenarios. It's also important to document the purpose of the new scenario in the main test's README.

The following files will be considered for a scenario:
```
- <pmacct-daemon>-XX.conf
- output-<name>-XX.json
- <map_type>.map              # not necessary to create an additional pmacct_mount folder here (will be handled by the framework)
```

All other files are specific to the test logic and cannot be changed. If you need to change the pcap or the test logic within XXX_test.py, you will need to create a new test!

## 5 - Debugging

To create the pmacct test network:
```shell
tools/start_network.sh
```

To start Kafka infrastructure (pmacct test network required):
```shell
tools/start_kafka.sh
```

To start Redis, if needed (pmacct test network required):
```shell
tools/start_redis.sh
```

To start pmacct with the EXACT configuration of a specific test case:
```shell
tools/start_pmacct_and_setup_test_case.sh <test_case_number>
e.g.
tools/start_pmacct_and_setup_test_case.sh 302
```

To play pcap file from a specific pcap folder (i.e., which contains a pcap file and a config file).
Note: the pcap folder must have been created in the corresponding results folder, 
if the start_pmacct script has been used for deploying pmacct:
```shell
tools/play_traffic.sh <full-path-to-pcap-folder> <IP address of the pcap player>
e.g.
tools/play_traffic.sh /<path>/pmacct-test-automation/results/200-BMP-HUAWEI-locrib_instance/pcap_mount_0 172.21.1.101
```
To play in detached mode:
```shell
tools/play_traffic_detached.sh <full-path-to-pcap-folder> <traffic_container_ID> <IP address of the pcap player>
e.g.
tools/play_traffic_detached.sh /<path>/pmacct-test-automation/results/200-BMP-HUAWEI-locrib_instance/pcap_mount_0 0 172.21.1.101
```

To display all available (pending) messages from a Kafka topic
(note: the actual Kafka topic name is listed in the pmacct config file in the results folder of the test case):
```shell
tools/get_pending_kafka_messages.sh <Kafka topic name> <Avro|PlainJson>
e.g.
tools/get_pending_kafka_messages.sh daisy.bmp.19f5021c Avro
```

### Hints

If no messages are received and reading times out, it is very probably that you are not using the correct consumer
object in the test. The framework creates as many consumers as the number of Kafka topics referenced in the pmacct
config file. 
The fixture consumer_setup_teardown returns the list of consumers created. The test method typically calls main with
either the consumer list, or the first consumer only- it's up to the test case author.

## 6 - Internals

### Fixtures

In [tests/conftest.py](tests/conftest.py) we define the following fixtures, i.e. functions that provide a fix baseline for initializing the tests:

**check_root_dir** makes sure pytest is run from the top level directory of the framework

**kafka_infra_setup_teardown** sets up (and tears down) kafka infrastructure

**prepare_test** creates results folder, pmacct_mount, etc. and copies all needed files there 
    edits pmacct config file with framework-specific details (IPs, ports, paths, etc.)

**pmacct_setup_teardown** sets up (and tears down) pmacct container itself

**prepare_pcap** edits pcap configuration file with framework-specific IPs and hostnames
              creates pcap_mount_n folders and copies traffic pcap and reproducer conf

**consumer_setup_teardown** creates and tears down the Kafka consumer (message reader)