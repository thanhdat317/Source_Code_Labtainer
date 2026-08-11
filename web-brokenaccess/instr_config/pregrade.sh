#!/bin/bash
homedir=$1
destdir=$2
cd $homedir/$destdir 2>/dev/null || true
here=`pwd`
mkdir -p $here/.local/result
exit 0
