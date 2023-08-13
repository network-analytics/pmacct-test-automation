# Network Analytics Test Framework

## How To Install

Create and activate Python virtual envirinment:
```shell
$ python -m venv venv
$ source ./venv/bin/activate
```

Install Python project dependencies:
```shell
$ pip install -r requirements.txt
```

Build single- and multi-pcap traffic reproducer images
```shell
$ cd tools/pcap_player
$ docker build -t traffic-reproducer -f single/Dockerfile .
$ docker build -t traffic-reproducer-multi -f multi/Dockerfile .
```

## How To Run

To run one or more test cases:
```shell
$ ./runtest.sh [--dry] [--loglevel=LOGLEVEL] <test case number or wildcard> [<test case number or wildcard> ...]
e.g.
$ ./runtest.sh 202 (run test 202 with default log level INFO)
$ ./runtest.sh 101 102 201 301 (run tests 101, 102, 201 and 301 with log level INFO)
$ ./runtest.sh --loglevel=INFO 2* (run all 2xx test cases with log level INFO)
$ ./runtest.sh * (run all test cases with log level INFO)
$ ./runtest.sh --dry --loglevel=DEBUG 4* (dry-run all 4xx test cases – the python pytest command will only be printed, not executed)

```

To run test cases with python and pytest (without the added functionality of ./runtests.sh):
```shell
$ python -m pytest tests/<test case name> --log-cli-level=<log level> --html=<report html file>
e.g.
$ python -m pytest tests/300-BGP-IPv6-CISCO-extNH_enc --log-cli-level=DEBUG --html=report.html

```

In exceptional situations, e.g. when setup or teardown fails or is stopped, there may be some remaining components left running.
To stop Kafka components, including the created network, do:
```shell
$ tools/stop_all.sh

```

Local folder results/<test case>/pmacct_mount is mounted on pmacct container's folder /var/log/pmacct

Local folder(s) results/<test case>/pcap_mount_n are mounted on traffic reproducer container's folder /pcap


## Debugging and Developing Test Cases

While at net_ana root directory,

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
tools/start_pmacct.sh <test_case_number>
e.g.
tools/start_pmacct.sh 302
```

## Fixtures explained

**check_root_dir** makes sure pytest is run from the top level directory of the framework

**kafka_infra_setup_teardown** sets up (and tears down) kafka infrastructure

**prepare_test** creates results folder, pmacct_mount, etc. and copies all needed files there 
    edits pmacct config file with framework-specific details (IPs, ports, paths, etc.)

**pmacct_setup_teardown** sets up (and tears down) pmacct container itself

**prepare_pcap** edits pcap configuration file with framework-specific IPs and hostnames
              creates pcap_mount_n folders and copies traffic pcap and reproducer conf

**consumer_setup_teardown** creates and tears down the Kafka consumer (message reader)

## Hints

If no messages are received and reading times out, it is very probably that you are not using the correct consumer
object in the test. The framework creates as many consumers as the number of Kafka topics referenced in the pmacct
config file.
The fixture consumer_setup_teardown returns the list of consumers created. The test method typically calls main with
either the consumer list, or the first consumer only- it's up to the test case author.