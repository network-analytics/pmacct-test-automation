#!/bin/bash
# Temporary solution until we integrate the framework in the pmacct repo
# Rootless containers --> discuss with Paolo

SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )

# Pull pmacct
#if [ ! -d $SCRIPT_DIR/pmacct ] ; then
#  git clone "https://github.com/rodonile/pmacct.git" $SCRIPT_DIR/pmacct
#fi

# Update source tree
cd $SCRIPT_DIR/pmacct
#git fetch origin
#git checkout master
#git pull

# TODO: make it available to change as a script argument (default local)
# TODO: make also repo url available (default master pmacct)
TAG='local'

echo "Building pmacct docker images"
docker build -t pmacct-base:$TAG -f $SCRIPT_DIR/base/Dockerfile $SCRIPT_DIR/pmacct || exit $?

docker build -t nfacctd:$TAG -f $SCRIPT_DIR/nfacctd/Dockerfile_non_root $SCRIPT_DIR/pmacct || exit $?
docker build -t pmbmpd:$TAG -f $SCRIPT_DIR/pmbmpd/Dockerfile_non_root $SCRIPT_DIR/pmacct || exit $?
docker build -t pmbgpd:$TAG -f $SCRIPT_DIR/pmbgpd/Dockerfile_non_root $SCRIPT_DIR/pmacct || exit $?
