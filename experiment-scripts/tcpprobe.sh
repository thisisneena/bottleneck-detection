#!/bin/bash

rm -f "$1"

control_c() {
    kill $TCPCAP
    exit
}

trap control_c SIGINT

sudo modprobe tcp_probe port=5001
cat /proc/net/tcpprobe > "$1" &
TCPCAP=$!

iperf -s -p 5001