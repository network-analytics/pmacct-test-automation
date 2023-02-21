#!/bin/bash

docker inspect --format="{{ .State.Running }}" "$1" 2>&1
