
#!/bin/bash

# exit if there is no argument
if [ -z "$1" ]; then
    echo "No argument supplied"
    exit 1
fi

cd "$(dirname "$0")"

files=( tests/${1}* )

# Check the length of the array
if [ ${#files[@]} -gt 1 ]; then
    echo "Wildcard pattern matched more than one entry"
    exit 1
fi

testdir=${files[0]}

python -m pytest tests/${1}* --log-cli-level=DEBUG --html=results/report${1}.html

mv results/report${1}.html ${testdir/tests/results}/
mv results/assets ${testdir/tests/results}/


