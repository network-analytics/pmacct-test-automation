#!/bin/bash

function handle_message()
{
  echo "Resource monitor received SIGUSR1, exiting"
  exit 0
}

# trapping the SIGINT signal
trap handle_message SIGUSR1

OUTPUT_FILE=$1

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

rm -f ${OUTPUT_FILE}

echo "Monitoring pmacct container resource needs -- outputting to file: $OUTPUT_FILE"

# No concurrency issues with test_name_logging fixture are expected, even though logging to the same file,
# because that fixture only logs before pmacct is deployed (since its scope is module)
while true; do
  if docker inspect pmacct >/dev/null 2>&1; then
    dte=$( date )
    msg=$( docker stats pmacct --no-stream --format '{{ json . }}' 2>/dev/null )
    if [ $? -eq 0 ]; then
      echo "$dte $msg" >> ${OUTPUT_FILE}
    fi
  fi
  sleep 1
done
