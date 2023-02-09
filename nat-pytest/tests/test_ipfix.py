import pytest
import scapy
import subprocess as subp

def ipfix_traffic_generator():
    command = 'sudo python ../traffic_generators/ipfix/play_ipfix_packets.py -S "10.1.1.1" -D "10" -F "15" -C "1" -w "10"'
    try:
        subp.check_call(command, shell=True)
        assert True
    except Exception:
        assert False
def test_run_ipfix_generator():
    ipfix_traffic_generator()