#!/bin/sh
#
homedir=$1
# destdir includes the container 
destdir=$2
dbg=/tmp/pregrade.log
cd $homedir/$destdir
here=`pwd`

case "$destdir" in
  *web-xss-server*)
    # Server-specific checks
    outpath=$here/.local/result
    mkdir -p "$outpath"
    db_file="/juice-shop_11.1.2/data/juiceshop.sqlite"
    if [ -f "$db_file" ]; then
       sqlite3 "$db_file" "SELECT email FROM Users;" > "$outpath/registered_users.txt" 2>>$dbg
       sqlite3 "$db_file" "SELECT file FROM Complaints;" > "$outpath/complaints_list.txt" 2>>$dbg
       sqlite3 "$db_file" "SELECT description FROM Products WHERE id = 2;" > "$outpath/product2_desc.txt" 2>>$dbg
       sqlite3 "$db_file" "SELECT price FROM Products WHERE id = 6;" > "$outpath/product6_price.txt" 2>>$dbg
    else
       echo "juiceshop database not found" >> $dbg
    fi
    ;;
  *web-xss*)
    # Client-specific checks
    is_sqlite=`which sqlite3`
    if [ ! -z "$is_sqlite" ]; then
       places=$here/.mozilla/firefox/*default/places.sqlite
       for fname in $places; do
         if [ -f "$fname" ]; then
            outpath=$here/.local/result
            outfile=$outpath/moz_places.txt
            mkdir -p "$outpath"
            sqlite3 "$fname" "SELECT moz_places.* FROM moz_places;" >"$outfile" 2>>$dbg
         fi
       done
    fi
    
    # Check for ZAP report
    outpath=$here/.local/result
    mkdir -p "$outpath"
    if [ -f "$here/report_zap.html" ] || [ -f "$here/report_zap" ] || [ -f "$here/Desktop/report_zap.html" ] || [ -f "$here/Desktop/report_zap" ]; then
       echo "zap_report_created" > "$outpath/zap_report.txt"
    else
       echo "zap_report_missing" > "$outpath/zap_report.txt"
    fi
    ;;
esac
