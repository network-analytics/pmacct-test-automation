#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
    echo "No argument supplied"
    exit 1
fi

DRY_RUN="FALSE"
if [[ "$1" == "--dry" ]]; then
  DRY_RUN="TRUE"
  shift
fi

LOG_LEVEL="INFO"
if [[ "$1" == "--loglevel="* ]]; then
  LOG_LEVEL=${1/--loglevel=/}
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
  echo "No test case(s) found"
  exit 1
fi

echo "Will run $count test files"

echo "Selected: $test_files"

if [ $count -eq 1 ]; then
  test="${test_files:6:3}"
  testdir=$( dirname $test_files )
  if [[ "$DRY_RUN" == "TRUE" ]]; then
    echo "python -m pytest $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog${test}.log --html=results/report${test}.html"
    exit 0
  fi
  python -m pytest $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog${test}.log --html=results/report${test}.html
  echo "Moving report to the test case specific folder"
  mv results/pytestlog${test}.log ${testdir/tests/results}/
  mv results/report${test}.html ${testdir/tests/results}/
  mv results/assets ${testdir/tests/results}/
else
  rm -rf results/assets
  rm -f results/report.html
  echo "Multiple files"
  if [[ "$DRY_RUN" == "TRUE" ]]; then
    echo "python -m pytest $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog.log --html=results/report.html"
    exit 0
  fi
  python -m pytest $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog.log --html=results/report.html
fi


