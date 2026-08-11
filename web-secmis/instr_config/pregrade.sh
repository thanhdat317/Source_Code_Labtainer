#!/bin/bash
homedir=$1
destdir=$2
cd $homedir/$destdir 2>/dev/null || true
here=`pwd`

case "$destdir" in
  *web-secmis*)
    outpath=$here/.local/result
    mkdir -p "$outpath"
    if [ -f "$here/Desktop/report.html" ] || [ -f "$here/report.html" ]; then
       echo "zap_report_spider_created" > "$outpath/zap_report_spider.txt"
    else
       echo "zap_report_spider_missing" > "$outpath/zap_report_spider.txt"
    fi
    if [ -f "$here/report_zap" ] || [ -f "$here/report_zap.html" ] || [ -f "$here/Desktop/report_zap" ] || [ -f "$here/Desktop/report_zap.html" ]; then
       echo "zap_report_final_created" > "$outpath/zap_report_final.txt"
    else
       echo "zap_report_final_missing" > "$outpath/zap_report_final.txt"
    fi
    ;;
esac
exit 0
