#!/bin/bash
rm -f iperf-client-*.log

echo "running $2 xtraffic flows..."
for (( i=0;i<$2;i++ ))
do
    iperf -c $MAHIMAHI_BASE -p 5001 -Z cubic -t $3 > /dev/null &
done

echo "running $1 nimbus flows..."
for (( i=1;i<$1;i++ ))
do
    iperf -c $MAHIMAHI_BASE -p 5001 -Z ccp -t $3 > "iperf-client-$i.log" &
done
iperf -c $MAHIMAHI_BASE -p 5001 -Z ccp -t $3 > "iperf-client-$1.log"
