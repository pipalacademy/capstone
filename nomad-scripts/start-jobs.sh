#! /bin/bash
#
# Script to start capstone system jobs in Nomad 
#

root=`dirname $0`

jobs=`ls $root/jobs/*.nomad.hcl | sort`

for f in $jobs
do
    echo "starting $f"
    nomad run $f
done 