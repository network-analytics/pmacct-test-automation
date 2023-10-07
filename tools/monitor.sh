#!/bin/bash

function handle_message()
{
  echo "Received SIGUSR1, exiting"
  exit 0
}

# trapping the SIGINT signal
trap handle_message SIGUSR1

OUTPUT_FILE=$1

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

rm -f ${OUTPUT_FILE}

echo "Monitoring pmacct container resource needs -- outputting to file: $OUTPUT_FILE"

while true; do
  if docker inspect pmacct >/dev/null 2>&1; then
    dte=$( date )
    msg=$( docker stats pmacct --no-stream --format '{{ json . }}' )
    if [ $? -eq 0 ]; then
      echo "$dte $msg" >> ${OUTPUT_FILE}
    fi
  fi
  sleep 1
done
