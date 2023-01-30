#!/bin/sh

# Build docker image
docker build -f ./Dockerfile_pytest -t python-nat-pytest .