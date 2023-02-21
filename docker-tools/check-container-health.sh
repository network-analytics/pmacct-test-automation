#!/bin/bash



docker inspect --format='{{json .State.Health.Status}}' "$1" 2>&1
