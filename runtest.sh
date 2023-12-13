#!/bin/bash

###################################################
# Automated Testing Framework for Network Analytics
# Pytest wrapper script for running test cases or
# groups thereof
# nikolaos.tsokas@swisscom.com 30/06/2023
###################################################

function handle_interrupt() {
  echo "Called handle_interrupt"
  tools/stop_all.sh
}

# trapping the SIGINT signal
trap handle_interrupt SIGINT

function print_help() {
  echo "Usage:   ./runtest.sh [--dry] [--loglevel=<log level>] [--mark=<expression>] [--key=<expression>] \
<test case number or wildcard>[:<scenario or wildcard>] [<TC number or wildcard>[:<scenario or wildcard>] ...]"
  echo
  echo "Examples: ./runtest.sh --loglevel=DEBUG 103 202"
  echo "          ./runtest.sh --dry 103:01 202:01 --key=cisco"
  echo
  echo "Script needs to be run from the top level directory of the testing framework"
}

function start_monitor() {
  tools/monitor.sh results/monitor.log $LOG_LEVEL &
  MONITOR_PID=$!
  [ "$LOG_LEVEL" = "DEBUG" ] && echo "Started pmacct monitor with pid $MONITOR_PID dumping to file results/monitor.log"
}

function stop_monitor() {
  kill -SIGUSR1 $MONITOR_PID
  [ "$LOG_LEVEL" = "DEBUG" ] && echo "Stopping pmacct monitor with pid $MONITOR_PID... "
  wait $MONITOR_PID
  [ "$LOG_LEVEL" = "DEBUG" ] && echo "Pmacct monitor stopped"
}

function run_pytest() {
  cmd="python3 -m pytest${MARKERS}${KEYS} ${test_files[@]} --runconfig=$RUNCONFIG --log-cli-level=$LOG_LEVEL \
--log-file=results/pytestlog.log --html=results/report.html"
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

lsout="$( ls | tr '\n' ' ')"
if [[ "$lsout" != *"library"*"pytest.ini"*"settings.conf"*"tests"*"tools"* ]]; then
  echo "Script not run from framework's root directory"
  print_help
  exit 1
fi

arg_was_asterisk=1; [[ "$@ " == *"$lsout"* ]] && arg_was_asterisk=0 # space after $@ needed!
DRY_RUN="FALSE"
source ./settings.conf # getting default LOG_LEVEL
MARKERS=
KEYS=
TESTS=()
for arg in "$@"
  do
    case $arg in
      '--help'|'-h') print_help; exit 0;;
      '--dry') DRY_RUN="TRUE";;
      '--loglevel='*) LOG_LEVEL=${arg/--loglevel=/};;
      '--mark='*) MARKERS=" -m \"${arg/--mark=/}\"";;
      '--key='*) KEYS=" -k \"${arg/--key=/}\"";;
      *) if [[ "$arg_was_asterisk" != "0" ]] || [[ "$lsout" != *"$arg "* ]]; then TESTS+=(${arg}); fi;;
    esac
  done

[[ "$arg_was_asterisk" == "0" ]] && TESTS+=("*:*")

args="${TESTS[@]}"
RUNCONFIG="${args// /_}"

test_files=()
for arg in "${TESTS[@]}"; do # getting the test case part
  arg="${arg%%:*}*"
  test_files+=( "tests/${arg/\*\*/*}" ) # remove double asterisk, just in case
done

count=${#TESTS[@]}
if [ $count -lt 1 ]; then
  echo "No tests found for arguments: $@"
  print_help
  exit 1
fi

rm -rf results/assets results/report.html results/pytestlog.log results/monitor.log
if [[ "$count" == "1" ]] && [[ "${TESTS[@]}" =~ ^[0-9]{3}:[0-9]{2}$ ]]; then # single-test run
  testandscenario="${TESTS[@]}"
  test="${testandscenario:0:3}"
  scenario="${testandscenario:4:2}"
  testdir=$( ls -d tests/*/ | grep "${test}-" | sed 's#/$##' )
  resultstestdir="${testdir/tests/results}"
  [[ "$scenario" != "00" ]] && resultstestdir="${resultstestdir}__scenario-$scenario"
  run_pytest
  retCode=$?
  cp -rf results/pytestlog.log results/report.html results/assets results/monitor.log ${resultstestdir}/ > /dev/null 2>&1
else # multi-test run
  run_pytest
  retCode=$?
fi
exit "$retCode"
