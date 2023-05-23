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

To run unit tests (root privileges are sometimes required by scapy library to send packets out):
```shell
$ sudo python -m pytest tests/smoke --log-cli-level=DEBUG --html=smokereport.html
OR
$ python -m pytest tests/001-IPFIXv10-cisco-T260+261 --log-cli-level=DEBUG --html=smokereport.html

```


Local folder pmacct_mount is mounted on pmacct container's folder /var/log/pmacct


## Debugging and Developing

While at net_ana root directory:

Do:
python -m pytest tests/skeleton/test.py -k 'test_start_kafka' --log-cli-level=DEBUG
for starting kafka

Do:
python -m pytest tests/skeleton/test.py -k 'test_start_pmacct' --log-cli-level=DEBUG
for starting pmacct

Do:
sudo python3 ./traffic_generators/ipfix/play_ipfix_packets.py -S 10.1.1.1 -D 1 -F 15 -C 1 -w 10 -p 2929
for sending ipfix packets for 1 second

Do:
python -m pytest tests/skeleton/test.py -k 'read' --log-cli-level=DEBUG
for reading available Kafka messages



Finally:
test_stop_pmacct
test_stop_kafka


For running all tests:
sudo python -m pytest -r tests/*/test.py --log-cli-level=DEBUG

