#!/bin/bash
homedir=$1
destdir=$2
cd $homedir/$destdir 2>/dev/null || true
here=`pwd`
case "$destdir" in
  *web-insdes.web-insdes.student*)
     outpath=$here/.local/result
     mkdir -p "$outpath"
     if [ -f "traversal.html" ] || [ -f "Desktop/traversal.html" ]; then
        echo "ZAP_REPORT_OK" > "$outpath/report_status.txt"
     else
        echo "NO_ZAP_REPORT" > "$outpath/report_status.txt"
     fi
     ;;
esac
exit 0
