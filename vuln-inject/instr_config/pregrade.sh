#!/bin/bash
homedir=$1
destdir=$2
cd $homedir/$destdir 2>/dev/null || true
here=`pwd`
if [[ "$destdir" == *"web-inject.student"* ]]; then
   outpath=$here/.local/result
   mkdir -p "$outpath"
   if [ -f "report_zap.html" ] || [ -f "report_zap" ] || [ -f "Desktop/report_zap.html" ] || [ -f "Desktop/report_zap" ]; then
      echo "ZAP_REPORT_OK" > "$outpath/report_status.txt"
   else
      echo "NO_ZAP_REPORT" > "$outpath/report_status.txt"
   fi
fi
exit 0
