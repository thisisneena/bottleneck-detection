#!/bin/bash
rm -f iperf-client-*.log

for (( i=1;i<$1;i++ ))
do
    iperf -c $MAHIMAHI_BASE -p 5001 -Z ccp -t 60 > "iperf-client-$i.log" &
done
echo "running $1 nimbus flows..."
iperf -c $MAHIMAHI_BASE -p 5001 -Z ccp -t 60