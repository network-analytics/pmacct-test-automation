#!/bin/sh

# Forcefully deleting all traffic containers

echo "Removing all traffic containers"
docker ps --all --filter name="traffic-reproducer-" --quiet | while read -r value; do docker rm --force "$value"; done 
