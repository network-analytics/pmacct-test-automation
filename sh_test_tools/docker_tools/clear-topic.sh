#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "{\"partitions\": [{\"topic\": \"$1\", \"partition\": 0, \"offset\": -1}], \"version\":1}" > $SCRIPT_DIR/clear-topic.json
if [[ $? -ne 0 ]] ; then
    exit 1
fi

docker cp $SCRIPT_DIR/clear-topic.json broker:/
if [[ $? -ne 0 ]] ; then
    exit 1
fi

docker exec broker /bin/kafka-delete-records --bootstrap-server broker:9092 --offset-json-file /clear-topic.json
