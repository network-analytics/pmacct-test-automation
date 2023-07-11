#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
    echo "No argument supplied"
    exit 1
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
else
  # argument was not an asterisk
  test_files=""
  for arg in "$@"; do
    test_files="$test_files $( ls -d tests/${arg}*/*test*.py )"
  done
  test_files="${test_files## }"
fi

count="$( echo "$test_files" | wc -l )"

#echo "Selected: $test_files"

if [ $count -eq 1 ]; then
  #echo "One file: $test_files"
  test="${test_files:6:3}"
  #echo "Test: $test"
  testdir=$( dirname $test_files )
  #echo "TestDir: $testdir"
  python -m pytest $test_files --log-cli-level=DEBUG --html=results/report${test}.html
  echo "Moving report to the test case specific folder"
  mv results/report${test}.html ${testdir/tests/results}/
  mv results/assets ${testdir/tests/results}/
else
  rm -rf results/assets
  rm -f results/report.html
  #echo "Multiple files"
  python -m pytest $test_files --log-cli-level=DEBUG --html=results/report.html
fi


