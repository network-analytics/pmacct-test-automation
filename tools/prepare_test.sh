#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
    echo "No argument supplied"
    exit 1
fi

cd "$(dirname "$0")"
cd ..
files=( tests/${1}* )
echo "${#files[@]}"

# Check the length of the array
if [ ${#files[@]} -gt 1 ]; then
    echo "Wildcard pattern tests/${arg}* matched more than one entry"
    exit 1
fi


