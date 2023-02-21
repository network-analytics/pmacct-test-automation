Traffic generator IPFIX
=====

## Dependencies
scappy version 2.5.0


## How to use:

usage:
```
play_ipfix_packets.py [-h] [-c COLLECTOR_IP] [-p COLLECTOR_PORT] -S START_IP -F PREFIX -C NUMBER_CLIENTS [-D TEST_DURATION] -w WAIT_TIME_MS
                             [WAIT_TIME_MS ...]
```

The required arguments are: 

-S/--start-ip, -F/--prefix, -C/--number-clients, -w/--wait-time-ms

## Working Example
with use of the defaults for the collectors IP and port:

```
sudo python play_ipfix_packets.py -S '10.1.1.1' -D '10' -F '15' -C '1' -w '10'
```
