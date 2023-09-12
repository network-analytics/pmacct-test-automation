#!/bin/bash
# Temporary solution until we integrate the framework in the pmacct repo
# Rootless containers --> discuss with Paolo

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

# Pull pmacct
if [ ! -d pmacct ] ; then
    git clone "https://github.com/pmacct/pmacct.git" $SCRIPT_DIR/pmacct
fi

# Update source tree
cd $SCRIPT_DIR/pmacct
git fetch origin
git pull

# Here we can eventually checkout to a specific commit-id if we need to
git checkout ec33571cd33897d16342ae07dcce6ec398680b57       # Daisy PROD target September 2023

echo "Building pmacct docker images"
docker build -t pmacct-base:local -f $SCRIPT_DIR/base/Dockerfile $SCRIPT_DIR/pmacct || exit $?
docker build -t nfacctd:local -f $SCRIPT_DIR/nfacctd/Dockerfile_non_root $SCRIPT_DIR/pmacct || exit $?
docker build -t pmbmpd:local -f $SCRIPT_DIR/pmbmpd/Dockerfile_non_root $SCRIPT_DIR/pmacct || exit $?
docker build -t pmbgpd:local -f $SCRIPT_DIR/pmbgpd/Dockerfile_non_root $SCRIPT_DIR/pmacct || exit $?
