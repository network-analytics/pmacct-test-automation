#!/bin/bash

docker exec broker /bin/kafka-run-class kafka.tools.GetOffsetShell --bootstrap-server broker:9092 --topic "$1"

