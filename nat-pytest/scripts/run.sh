#!/bin/sh

# Run docker container on your local environment
docker run -i --rm --log-driver=none -a stdin -a stdout -a stderr --name pytest_img -p 8000:8000 python-nat-pytest
