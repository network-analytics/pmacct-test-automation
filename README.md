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

## How To Run

To run on or more test cases:
```shell
$ ./runtest.sh [--dry] [--loglevel=LOGLEVEL] <test case number or wildcard> [<test case number or wildcard> ...]
e.g.
$ ./runtest.sh 202 (run test 202 with default log level DEBUG)
$ ./runtest.sh 101 102 201 301 (run tests 101, 102, 201 and 301 with log level DEBUG)
$ ./runtest.sh --loglevel=INFO 2* (run all 2xx test cases with log level INFO)
$ ./runtest.sh * (run all test cases with log level DEBUG)
$ ./runtest.sh --dry --loglevel=INFO 4* (dry-run all 4xx test cases – the python pytest command will only be printed, not executed)

```

To run test cases with python and pytest:
```shell
$ python -m pytest tests/<test case name> --log-cli-level=<log level> --html=<report html file>
e.g.
$ python -m pytest tests/001-IPFIXv10-cisco-T260+261 --log-cli-level=DEBUG --html=smokereport.html

```


Local folder results/<test case>/pmacct_mount is mounted on pmacct container's folder /var/log/pmacct

Local folder(s) results/<test case>/pcap_mount_n are mounted on traffic reproducer container's folder /pcap


## Debugging and Developing

While at net_ana root directory,

To create the pmacct test network:
```shell
library/sh/test_network/create.sh
```

To start Kafka infrastructure (pmacct test network required):
```shell
library/sh/kafka_compose/start.sh
```

To send ipfix packets for 1 second
```shell
sudo python3 ./traffic_generators/ipfix/play_ipfix_packets.py -S 10.1.1.1 -D 1 -F 15 -C 1 -w 10 -p 2929
```

Do:
python -m pytest tests/skeleton/test.py -k 'read' --log-cli-level=DEBUG
for reading available Kafka messages

To stop pmacct:
```shell
library/sh/pmacct_docker/stop.sh
```

To stop Kafka infrastructure:
```shell
library/sh/kafka_compose/stop.sh
```

To delete pmacct_test_network:
```shell
library/sh/test_network/delete.sh
```

To run all tests (make sure to first delete existing results/assets and results/report.html):
```shell
python -m pytest -r tests/*/test.py --log-cli-level=INFO --html=results/report.html
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