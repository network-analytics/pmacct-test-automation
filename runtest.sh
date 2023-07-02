#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
    echo "No argument supplied"
    exit 1
fi

cd "$(dirname "$0")"

for arg in "$@"; do
  files=( tests/${arg}* )
  # Check the length of the array
  if [ ${#files[@]} -gt 1 ]; then
      echo "Wildcard pattern tests/${arg}* matched more than one entry"
      exit 1
  fi
done

if [ "$#" -gt 1 ]; then
  args=""
  for arg in "$@"; do
    args="$args tests/${arg}*"
  done
  rm -rf results/assets
  rm -f results/report.html
  python -m pytest $args --log-cli-level=DEBUG --html=results/report.html
else
  python -m pytest tests/${1}* --log-cli-level=DEBUG --html=results/report${1}.html
  testdir=${files[0]}
  echo "Moving report to the test case specific folder"
  mv results/report${1}.html ${testdir/tests/results}/
  mv results/assets ${testdir/tests/results}/
fi
