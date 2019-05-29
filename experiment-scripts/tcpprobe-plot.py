#!/usr/bin/python2

import matplotlib, sys
matplotlib.use('Agg')

from tcpprobe_plot import *

if __name__ == '__main__':
    fname = sys.argv[1]
    print "Loading data..."
    df = import_tcp_probe_data(fname)
    switches_by_flow = get_switches("../nimbus/nimbus-err2.log")

    print "Plotting cwnd for all data..."
    plot(df, switches_by_flow, "snd_cwnd", "multiple-nimbus-cwnd-1")
    print "Plotting rtt for all data..."
    plot(df, switches_by_flow, "srtt", "multiple-nimbus-rtt-1")


