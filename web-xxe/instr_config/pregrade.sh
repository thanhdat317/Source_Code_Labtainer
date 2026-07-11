#!/bin/bash
# Record the required student-side report artifact before grading.
homedir="$1"
destdir="$2"
here="$homedir/$destdir"

if [ -f "$here/report_zap.html" ] || [ -f "$here/report_zap" ]; then
    mkdir -p "$here/.local/result"
    printf 'report_zap=present\n' > "$here/.local/result/report_status.txt"
fi

exit 0
