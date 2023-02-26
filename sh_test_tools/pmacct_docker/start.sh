#!/bin/sh

PMACCTD_CONF="$1"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#PMACCTD_CONF="$SCRIPT_DIR/pmacctd.conf"
LIBRDKAFKA_CONF="$SCRIPT_DIR/librdkafka.conf"
OUT_AVRO_SCHEMA_FOLDER="$SCRIPT_DIR/output_schema_folder"
#echo "$SCRIPT_DIR\n$PMACCTD_CONF\n$LIBRDKAFKA_CONF\n$OUT_AVRO_SCHEMA_CONF"

docker inspect --format="{{ .State.Running }}" pmacct >/dev/null 2>&1
if [ $? -ne 1 ]; then
  docker rm pmacct
fi

docker run -v "$PMACCTD_CONF":/etc/pmacct/nfacctd.conf \
           -v "$LIBRDKAFKA_CONF":/etc/pmacct/maps_dev/librdkafka.conf \
           -v "$OUT_AVRO_SCHEMA_FOLDER":/var/log/pmacct/avsc \
           --network pmacct_test_network \
           -p 2929:8989/udp \
           --name pmacct \
           remote-docker.artifactory.swisscom.com/pmacct/nfacctd >/dev/null 2>&1 &
