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

To run unit tests (root privileges are required by scapy library to send packets out):
```shell
$ sudo python -m pytest smoke_suite/smoke_suite.py --log-cli-level=DEBUG --html=smokereport.html
```


Local folder pmacct_mount is mounted on pmacct container's folder /var/log/pmacct


## Debugging
While at top directory:

Do:
sudo python3 ./traffic_generators/ipfix/play_ipfix_packets.py -S 10.1.1.1 -D 1 -F 15 -C 1 -w 10 -p 2929
for sending ipfix packets for 1 second

Do:
export PYTHONPATH=$(pwd); python3 ./smoke_suite/read_messages.py
for reading available Kafka messages

sudo python -m pytest -r tests/*/test.py --log-cli-level=DEBUG

