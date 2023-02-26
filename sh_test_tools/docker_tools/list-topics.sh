#!/bin/bash

docker exec broker /bin/kafka-topics --bootstrap-server broker:9092 --list

