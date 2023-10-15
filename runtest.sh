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
  cmd="python3 -m pytest${MARKERS}${KEYS} ${test_files[@]} --runconfig $RUNCONFIG --log-cli-level=$LOG_LEVEL \
--log-file=results/pytestlog${test}.log --html=results/report${test}.html"
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
<test case number or wildcard>[:<scenario or wildcard>] [<TC number or wildcard>[:<scenario or wildcard>] ...]"
  echo "Example: ./runtest.sh --loglevel=DEBUG 103 202"
  echo "         ./runtest.sh --dry 103:01 202:01 --key=cisco"
  exit 1
fi

init_args="$@"
lsout="$( ls | tr '\n' ' ')"
if [[ "$lsout" != *"library"*"pytest.ini"*"settings.conf"*"tests"*"tools"* ]]; then
  echo "Script not run from framework's root directory"
  exit 1
fi

arg_was_asterisk=1; [[ "$@ " == *"$lsout"* ]] && arg_was_asterisk=0
DRY_RUN="FALSE"
source ./settings.conf # getting default LOG_LEVEL
MARKERS=
KEYS=
TESTS=()
for arg in "$@"
  do
    case $arg in
      '--dry') DRY_RUN="TRUE" ; shift;;
      '--loglevel='*) LOG_LEVEL=${arg/--loglevel=/} ; shift;;
      '--mark='*) MARKERS=" -m \"${arg/--mark=/}\"" ; shift;;
      '--key='*) KEYS=" -k \"${arg/--key=/}\"" ; shift;;
      *) if [[ "$arg_was_asterisk" != "0" ]] || [[ "$lsout" != *"$arg "* ]]; then echo "Adding: $arg"; TESTS+=(${arg}); fi;;
    esac
  done

[[ "$arg_was_asterisk" == "0" ]] && TESTS+=("*:*")

args="${TESTS[@]}"
RUNCONFIG="${args// /_}"

test_files=()
for arg in "${TESTS[@]}"; do
  arg="${arg%%:*}*"
  test_files+=( "tests/${arg/\*\*/*}" )
done

count=${#TESTS[@]}
if [ $count -lt 1 ]; then
  echo "No tests found for arguments: $init_args"
  exit 1
fi

if [[ "$count" == "1" ]] && [[ "${TESTS[@]}" =~ ^[0-9]{3}:[0-9]{2}$ ]]; then
  echo "Single test run"
  testandscenario="${TESTS[@]}"
  test="${testandscenario:0:3}"
  scenario="${testandscenario:4:2}"
  testdir=$( ls -d tests/*/ | grep "${test}-" | sed 's#/$##' )
  resultstestdir="${testdir/tests/results}"
  [[ "$scenario" != "00" ]] && resultstestdir="${resultstestdir}__scenario-$scenario"
  run_pytest
  retCode=$?
  rm -rf ${resultstestdir}/assets
  mv results/pytestlog${test}.log results/report${test}.html results/assets $monitor_log ${resultstestdir}/ > /dev/null 2>&1
else
  echo "Multiple test run"
  rm -rf results/assets results/report.html
  run_pytest
  retCode=$?
fi
exit "$retCode"
