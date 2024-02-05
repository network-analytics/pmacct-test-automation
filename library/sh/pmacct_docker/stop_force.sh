#!/bin/bash

# stop each pmacct container, and if successful, remove the container completely

docker ps -aqf "name=nfacctd|pmbmpd|pmbgpd" | while read -r value; do
  docker stop $value && docker rm $value
done
