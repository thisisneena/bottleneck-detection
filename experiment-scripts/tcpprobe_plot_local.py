#!/usr/bin/python2
import matplotlib
matplotlib.use('tkagg')

import sys
from tcpprobe_plot import *

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Need two arguments: filename of tcpprobe output and filename of nimbus output")
        sys.exit(1)

    fname = sys.argv[1]
    nimbus_log = sys.argv[2]

    print("Loading data...")
    df = import_tcp_probe_data(fname)
    switches_by_flow = get_switches(nimbus_log)
    elasticity_data = get_ewma_elasticity(nimbus_log, time_shift=df["tv_sec"].min())
    if len(sys.argv) >= 4:
        n = int(sys.argv[3])
        print("Sampling every {}th row".format(n))
        df = df.iloc[::n, :]

    print("Plotting cwnd for all data...")
    plot(df, switches_by_flow, "snd_cwnd", elasticity_data=elasticity_data)
    print("Plotting rtt for all data...")
    plot(df, switches_by_flow, "srtt")
    print("Done! Type 'q' to finish viewing...")

    while True:
        if (sys.version_info > (3, 0)):
            x = input("")
        else:
            x = raw_input("")
        if x == "q":
            print("Closing session...")
            break



