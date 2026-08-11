#!/bin/bash
homedir=$1
destdir=$2
cd $homedir/$destdir 2>/dev/null || true
here=`pwd`
mkdir -p $here/.local/result

if [ -f $here/report_zap.html ] || [ -f $here/report_zap.htm ] || [ -f $here/report_zap ] || [ -f $here/Desktop/report_zap.html ] || [ -f $here/Desktop/traversal.html ]; then
    echo "zap_report_created" > $here/.local/result/zap_report.txt
fi

if [ -f $here/exploit.zip ] || [ -f $here/Desktop/exploit.zip ]; then
    echo "zip_exploit_created" > $here/.local/result/zip_exploit.txt
fi
exit 0
