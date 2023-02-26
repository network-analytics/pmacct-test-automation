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
$ sudo python -m pytest -s smoke_suite/smoke_suite.py 
```
