###################################################
# Automated Testing Framework for Network Analytics
# Pytest wrapper script for running test cases or
# groups thereof
# nikolaos.tsokas@swisscom.com 30/06/2023
###################################################

#!/bin/bash


function handle_interrupt()
{
  echo "Called handle_interrupt"
  tools/stop_all.sh
}

# trapping the SIGINT signal
trap handle_interrupt SIGINT

function start_monitor()
{
  monitor_log="results/monitor.log"
  tools/monitor.sh $monitor_log &
  MONITOR_PID=$!
  echo "Started pmacct monitor with pid $MONITOR_PID dumping to file $monitor_log"
}

function stop_monitor() {
  kill -SIGUSR1 $MONITOR_PID
  echo "Stopping pmacct monitor with pid $MONITOR_PID... "
  wait $MONITOR_PID
  echo "Pmacct monitor stopped"
}

function run_pytest() {
  cmd="python3 -m pytest${MARKERS}${KEYS}${SCENARIO} ${test_files[@]} --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog${test}.log --html=results/report${test}.html"
  if [ "$DRY_RUN" = "TRUE" ]; then
    echo -e "\nCommand to execute:\n$cmd\n\npytest dry run (collection-only):"
    cmd="$cmd --collect-only"
  else
    start_monitor
  fi
  eval "$cmd"
  retCode=$?
  [ "$DRY_RUN" = "TRUE" ] || stop_monitor
  return $retCode
}

# exit if there is no argument
if [ -z "$1" ]; then
  echo "No argument supplied"
  echo "Usage:   ./runtest.sh [--dry] [--loglevel=<log level>] [--mark=<expression>] [--key=<expression>] \
[--scenario=<scenario>] <test case number> [<test_case_number> ...]"
  echo "Example: ./runtest.sh --loglevel=DEBUG 103 202"
  echo "         ./runtest.sh --dry 103 202 --key=cisco"
  exit 1
fi

init_args="$@"
lsout="$( ls | tr '\n' ' ')"
if [[ "$lsout" != *"library"*"pytest.ini"*"settings.conf"*"tests"*"tools"* ]]; then
  echo "Script not run from net_ana root directory"
  exit 1
fi

DRY_RUN="FALSE"
source ./settings.conf # getting default LOG_LEVEL
MARKERS=
KEYS=
SCENARIO=
TESTS=()
for arg in "$@"
  do
    case $arg in
      '--dry') DRY_RUN="TRUE" ; shift;;
      '--loglevel='*) LOG_LEVEL=${arg/--loglevel=/} ; shift;;
      '--mark='*) MARKERS=" -m \"${arg/--mark=/}\"" ; shift;;
      '--key='*) KEYS=" -k \"${arg/--key=/}\"" ; shift;;
      '--scenario='*) SCENARIO=" --scenario ${arg/--scenario=/}" ; shift;;
      *) TESTS+=(${arg});;
    esac
  done

if [[ "${TESTS[@]} " == "$lsout"  ]]; then
  # argument was an asterisk
  test_files=($( ls -d tests/**/*test*.py 2>/dev/null ))
else
  # argument was not an asterisk
  test_files=()
  for arg in "${TESTS[@]}"; do
    test_files+=( $( ls -d tests/${arg}*/*test*.py 2>/dev/null ))
  done
fi

count=${#test_files[@]}
if [ $count -lt 1 ]; then
  echo "No test case(s) found for: $init_args"
  exit 1
fi

echo "Will run $count test files"
echo "Test files: ${test_files[@]}"
if [ $count -eq 1 ]; then
  test_file=${test_files[0]}
  test="${test_file:6:3}"
  echo "Single test run: ${test}"
  testdir=$( dirname $test_file )
  resultstestdir=${testdir/tests/results}
  run_pytest
  retCode=$?
  rm -rf ${resultstestdir}/assets
  mv results/pytestlog${test}.log results/report${test}.html results/assets $monitor_log ${resultstestdir}/ > /dev/null 2>&1
else
  if [ ! -z "$SCENARIO" ]; then
    echo "Scenarios not supported in multi-test-case runs"
    exit 1
  fi
  test=""
  echo "Multiple test run"
  rm -rf results/assets results/report.html
  run_pytest
  retCode=$?
fi
exit "$retCode"
