#!/bin/sh

ID="$1"

# stop container, and if successful, remove the container completely
docker stop traffic-reproducer-"$ID" && docker rm traffic-reproducer-"$ID"
