###################################################
# Automated Testing Framework for Network Analytics
# Pytest wrapper script for running test cases or
# groups thereof
# nikolaos.tsokas@swisscom.com 30/06/2023
###################################################

#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
    echo "No argument supplied"
    echo "Usage:   ./runtest.sh [--loglevel=<log level>] [--dry] <test case number> [<test_case_number> ...]"
    echo "Example: ./runtest.sh --loglevel=DEBUG 103 202"
    exit 1
fi

if [[ "${PWD##*/}" != "net_ana" ]]; then
  echo "Script not run from net_ana root directory"
  exit 1
fi

DRY_RUN="FALSE"
if [[ "$1" == "--dry" ]]; then
  DRY_RUN="TRUE"
  shift
fi


source ./settings.conf
#LOG_LEVEL="INFO"
if [[ "$1" == "--loglevel="* ]]; then
  LOG_LEVEL=${1/--loglevel=/}
  shift
fi

myarg="$( echo "$@ " )"
lsout="$( ls | tr '\n' ' ')"

if [[ "$myarg" == "$lsout"  ]]; then
  # argument was an asterisk
  test_files="$( ls -d tests/**/*test*.py 2>/dev/null )"
  test_files=$( echo "$test_files" | awk '{printf "%s ", $0}' | tr -d '\n' | sed 's/ $/\n/' )
else
  # argument was not an asterisk
  test_files=""
  for arg in "$@"; do
    test_files="$test_files $( ls -d tests/${arg}*/*test*.py 2>/dev/null )"
  done
  test_files="${test_files## }"
fi

count="$( echo "$test_files" | wc -w )"

if [ $count -lt 1 ]; then
  echo "No test case(s) found for: $myarg"
  exit 1
fi

echo "Will run $count test files"

echo "Selected: $test_files"

if [ $count -eq 1 ]; then
  test="${test_files:6:3}"
  testdir=$( dirname $test_files )
  cmd="python3 -m pytest $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog${test}.log --html=results/report${test}.html"
  if [[ "$DRY_RUN" == "TRUE" ]]; then
    echo "$cmd"
    exit 0
  fi
  eval "$cmd"
  retCode=$?
  echo "Moving report to the test case specific folder"
  mv results/pytestlog${test}.log ${testdir/tests/results}/
  mv results/report${test}.html ${testdir/tests/results}/
  rm -rf ${testdir/tests/results}/assets
  mv results/assets ${testdir/tests/results}/
else
  rm -rf results/assets
  rm -f results/report.html
  echo "Multiple files"
  cmd="python3 -m pytest $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog.log --html=results/report.html"
  if [[ "$DRY_RUN" == "TRUE" ]]; then
    echo "$cmd"
    exit 0
  fi
  eval "$cmd"
  retCode=$?
fi
exit "$retCode"

