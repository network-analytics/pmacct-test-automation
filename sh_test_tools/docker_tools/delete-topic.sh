#!/bin/bash

docker exec broker /bin/kafka-topics --bootstrap-server broker:9092 --delete --topic $1

