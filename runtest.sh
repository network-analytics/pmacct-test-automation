###################################################
# Automated Testing Framework for Network Analytics
# Pytest wrapper script for running test cases or
# groups thereof
# nikolaos.tsokas@swisscom.com 30/06/2023
###################################################

#!/bin/bash

#function stop_monitor()
#{
#  echo "Called stop_monitor"
#  if [ -n "$MONITOR_PID" ]; then
#    echo "Stopping pmacct monitor with pid $MONITOR_PID"
#    kill -9 $MONITOR_PID
#  fi
#}

function handle_interrupt()
{
  echo "Called handle_interrupt"
#  stop_monitor
  tools/stop_all.sh
}

# trapping the SIGINT signal
trap handle_interrupt SIGINT

# exit if there is no argument
if [ -z "$1" ]; then
  echo "No argument supplied"
  echo "Usage:   ./runtest.sh [--dry] [--loglevel=<log level>] [--mark=<expression>] [--key=<expression>] \
      <test case number> [<test_case_number> ...]"
  echo "Example: ./runtest.sh --loglevel=DEBUG 103 202"
  exit 1
fi

lsout="$( ls | tr '\n' ' ')"

if [[ "$lsout" != *"library"*"pytest.ini"*"settings.conf"*"tests"*"tools"* ]]; then
  echo "Script not run from net_ana root directory"
  exit 1
fi

DRY_RUN="FALSE"
if [[ "$1" == "--dry" ]]; then
  DRY_RUN="TRUE"
  shift
fi

source ./settings.conf # getting default LOG_LEVEL
if [[ "$1" == "--loglevel="* ]]; then
  LOG_LEVEL=${1/--loglevel=/}
  shift
fi

MARKERS=
if [[ "$1" == "--mark="* ]]; then
  echo "1: $1"
  MARKERS="-m \"${1/--mark=/}\""
  echo "Markers: $MARKERS"
  shift
fi

KEYS=
if [[ "$1" == "--key="* ]]; then
  echo "1: $1"
  KEYS="-k \"${1/--key=/}\""
  echo "Markers: $KEYS"
  shift
fi

myarg="$( echo "$@ " )"

if [[ "$myarg" == "$lsout"  ]]; then
  # argument was a plain asterisk
  test_files="$( ls -d tests/**/*test*.py 2>/dev/null )"
else
  # argument was not an asterisk
  test_files=""
  for arg in "$@"; do
    test_files="$test_files $( ls -d tests/${arg}*/*test*.py 2>/dev/null )"
  done
fi
test_files=$( echo "$test_files" | awk '{printf "%s ", $0}' | tr -d '\n' | sed 's/ $/\n/' )
while [[ "$test_files" == " "* ]]; do
  test_files="${test_files## }"
done

count="$( echo "$test_files" | wc -w )"

if [ $count -lt 1 ]; then
  echo "No test case(s) found for: $myarg"
  exit 1
fi

echo "Will run $count test files"

echo "Test files: $test_files"

#monitor_log="results/monitor.log"
#tools/monitor.sh $monitor_log &
#MONITOR_PID=$!
#echo "Started pmacct monitor with pid $MONITOR_PID dumping to file $monitor_log"

if [ $count -eq 1 ]; then
  test="${test_files:6:3}"
  echo "Single test run: ${test}"
  testdir=$( dirname $test_files )
  resultsdir=${testdir/tests/results}
  cmd="python3 -m pytest $MARKERS $KEYS $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog${test}.log --html=results/report${test}.html"
  if [[ "$DRY_RUN" == "TRUE" ]]; then
    echo
    echo "Command to execute:"
    echo "$cmd"
    echo
    echo "pytest dry run (collection-only):"
    eval "$cmd --collect-only"
    exit 0
  fi
  eval "$cmd"
  retCode=$?
  # if retCode==2, then pytest has received SIGINT signal, and therefore runtest will receive it, too
#  if [ $retCode -ne 2 ]; then
#    stop_monitor
#  fi
  if [ -d $resultstestdir ]; then
    echo "Moving files to the test case specific folder: $resultstestdir/"
    mv results/pytestlog${test}.log ${$resultstestdir}/
    mv results/report${test}.html ${$resultstestdir}/
    rm -rf ${$resultstestdir}/assets
    mv results/assets ${$resultstestdir}/
#    mv $monitor_log ${$resultstestdir}/
  fi
else
  echo "Multiple test run"
  rm -rf results/assets
  rm -f results/report.html
  echo "Multiple files"
  cmd="python3 -m pytest $MARKERS $KEYS $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog.log --html=results/report.html"
  if [[ "$DRY_RUN" == "TRUE" ]]; then
    echo
    echo "Command to execute:"
    echo "$cmd"
    echo
    echo "pytest dry run (collection-only):"
    eval "$cmd --collect-only"
    exit 0
  fi
  eval "$cmd"
  retCode=$?
  # if retCode==2, then pytest has received SIGINT signal, and therefore runtest will receive it, too
#  if [ $retCode -ne 2 ]; then
#    stop_monitor
#  fi
fi
exit "$retCode"
