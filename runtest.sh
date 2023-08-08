#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
    echo "No argument supplied"
    exit 1
fi

LOG_LEVEL="DEBUG"
if [[ "$1" == "-loglevel="* ]]; then
  LOG_LEVEL=${1/-loglevel=/}
  shift
fi

if [[ "${PWD##*/}" != "net_ana" ]]; then
  echo "Script not run from net_ana root directory"
  exit 1
fi

myarg="$( echo "$@ " )"
lsout="$( ls | tr '\n' ' ')"

if [[ "$myarg" == "$lsout"  ]]; then
  # argument was an asterisk
  test_files="$( ls -d tests/**/*test*.py )"
  test_files=$( echo "$test_files" | awk '{printf "%s ", $0}' | tr -d '\n' | sed 's/ $/\n/' )
else
  # argument was not an asterisk
  test_files=""
  for arg in "$@"; do
    test_files="$test_files $( ls -d tests/${arg}*/*test*.py )"
  done
  test_files="${test_files## }"
fi

count="$( echo "$test_files" | wc -w )"

echo "Will run $count test files"

echo "Selected: $test_files"

if [ $count -eq 1 ]; then
  #echo "One file: $test_files"
  test="${test_files:6:3}"
  #echo "Test: $test"
  testdir=$( dirname $test_files )
  #echo "TestDir: $testdir"
  python -m pytest $test_files --log-cli-level=$LOG_LEVEL --html=results/report${test}.html
  echo "Moving report to the test case specific folder"
  mv results/report${test}.html ${testdir/tests/results}/
  mv results/assets ${testdir/tests/results}/
else
  rm -rf results/assets
  rm -f results/report.html
  echo "Multiple files"
  python -m pytest $test_files --log-cli-level=$LOG_LEVEL --html=results/report.html
fi


