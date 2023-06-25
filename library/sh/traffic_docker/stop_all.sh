#!/bin/sh

# Forcefully deleting all traffic containers

echo "Removing all traffic containers"
docker ps --all --filter name="traffic-reproducer-" --quiet | xargs docker rm --force
