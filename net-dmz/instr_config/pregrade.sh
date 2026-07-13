#!/bin/bash
: <<'END'
This software was created by United States Government employees at 
The Center for Cybersecurity and Cyber Operations (C3O) 
at the Naval Postgraduate School NPS.  Please note that within the 
United States, copyright protection is not available for any works 
created  by United States Government employees, pursuant to Title 17 
United States Code Section 105.   This software is in the public 
domain and is not subject to copyright. 
END
#
# Script to run prior to grading a student's lab.  It is intended
# for two potential purposes:
# 1) Create solution artifacts to campare against student artifacts;
# 2) Process student artifacts into a different form, e.g., extracting
#    browser sqlite data as in the default instance of this file below.
# 
# 
#
homedir=$1
# destdir includes the container
destdir=$2
here="$homedir/$destdir"
outpath="$here/.local/result"
mkdir -p "$outpath"

# The grade container is ws1.  Preserve a short, human-readable summary in
# addition to the raw prestop evidence used by results.config.
{
    echo "net-dmz pregrade report"
    date -u +"generated_utc=%Y-%m-%dT%H:%M:%SZ"
    for artifact in local_nmap.txt internet_wget.txt; do
        if [[ -s "$outpath/$artifact" ]]; then
            echo "$artifact=present"
        else
            echo "$artifact=missing"
        fi
    done
} >"$outpath/report_status.txt"
