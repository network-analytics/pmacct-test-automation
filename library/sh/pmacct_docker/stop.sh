#!/bin/bash

# stop pmacct container, and if successful, remove the container completely
docker stop pmacct && docker rm pmacct
