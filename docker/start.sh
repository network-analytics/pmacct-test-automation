#!/bin/sh

PMACCTD_CONF="$(pwd)/pmacctd.conf" LIBRDKAFKA_CONF="$(pwd)/librdkafka.conf" OUT_AVRO_SCHEMA_CONF="$(pwd)/output_schema.avsc" docker-compose up
