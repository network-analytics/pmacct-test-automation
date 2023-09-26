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
source ./settings.conf # getting default LOG_LEVEL
MARKERS=
KEYS=
for arg in "$@"
  do
    case $arg in
      '--dry') DRY_RUN="TRUE" ; shift;;
      '--loglevel='*) LOG_LEVEL=${arg/--loglevel=/} ; shift;;
      '--mark='*) MARKERS=" -m \"${arg/--mark=/}\"" ; shift;;
      '--key='*) KEYS=" -k \"${arg/--key=/}\"" ; shift;;
      *) ;;
    esac
  done

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

# make a one-line list with single space between filenames
test_files=$( echo "$test_files" | awk '{printf "%s ", $0}' | tr -d '\n' | xargs )

count="$( echo "$test_files" | wc -w )"
if [ $count -lt 1 ]; then
  echo "No test case(s) found for: $myarg"
  exit 1
fi

echo "Will run $count test files"
echo "Test files: $test_files"

function run_pytest() {
  cmd="python3 -m pytest${MARKERS}${KEYS} $test_files --log-cli-level=$LOG_LEVEL --log-file=results/pytestlog${test}.log --html=results/report${test}.html"
  if [[ "$DRY_RUN" == "TRUE" ]]; then
    echo -e "\nCommand to execute:\n$cmd\n\npytest dry run (collection-only):"
    cmd="$cmd --collect-only"
  fi
  eval "$cmd"
}

if [ $count -eq 1 ]; then
  test="${test_files:6:3}"
  echo "Single test run: ${test}"
  testdir=$( dirname $test_files )
  resultstestdir=${testdir/tests/results}
  run_pytest
  retCode=$?
  if [ -d $resultstestdir ]; then
    echo "Moving files to the test case specific folder: $resultstestdir/"
    mv results/pytestlog${test}.log ${resultstestdir}/
    mv results/report${test}.html ${resultstestdir}/
    rm -rf ${resultstestdir}/assets
    mv results/assets ${resultstestdir}/
  fi
else
  test=""
  echo "Multiple test run"
  rm -rf results/assets
  rm -f results/report.html
  run_pytest
  retCode=$?
fi
exit "$retCode"
