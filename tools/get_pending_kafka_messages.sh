#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
  echo "Kafka topic name needs to be passed as argument"
  exit 1
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

cat > reader.py << EOL
from library.py.kafka_consumer import KMessageReader
import json, time
reader = KMessageReader('daisy.bmp.19f5021c')
time.sleep(1)
reader.connect()
time.sleep(1)
print('About to read')
time.sleep(1)
messages = reader.get_all_messages(2)
time.sleep(1)
print('Read ' + str(len(messages)) + ' messages')
time.sleep(1)
for msg in messages:
  print(json.dumps(msg))
EOL

python reader.py

rm reader.py
