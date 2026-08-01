#!/bin/bash
homedir=$1
destdir=$2
cd $homedir/$destdir
here=`pwd`

is_sqlite=`which sqlite3`
if [ ! -z $is_sqlite ]; then
   places=$here/.mozilla/firefox/*default/places.sqlite
   for fname in $(ls $places 2> /dev/null); do
     if [[ -f $fname ]]; then
        outpath=$here/.local/result
        outfile=$outpath/moz_places.txt
        mkdir -p "$outpath"
        sqlite3 "$fname" "SELECT moz_places.* FROM moz_places;" >"$outfile"
     fi
   done
fi

mkdir -p $here/.local/result
if [ -f $here/report_zap.html ] || [ -f $here/report_zap.htm ] || [ -f $here/report_zap ] || [ -f $here/Desktop/report_zap.html ] || [ -f $here/Desktop/traversal.html ]; then
    echo "zap_report_created" > $here/.local/result/zap_report.txt
fi

if [ -f $here/exploit.zip ] || [ -f $here/Desktop/exploit.zip ]; then
    echo "zip_exploit_created" > $here/.local/result/zip_exploit.txt
fi
