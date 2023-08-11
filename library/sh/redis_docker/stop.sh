#!/bin/sh

# stop redis container, and if successful, remove the container completely
docker stop redis && docker rm redis
