#!/usr/bin/python2

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys, re

switches_by_flow = None

def get_switches(fname, num_flows):
    switches = {}
    with open(fname) as f:
        start = None
        for l in f.readlines():
            if "DEBG Switch To" in l:
                flow_id = int(re.search(r"ID: (\d+)", l).group(1))
                elapsed = int(re.search(r"elapsed: (\d+)", l).group(1))
                if flow_id not in switches:
                    switches[flow_id] = [0]
                switches[flow_id].append(elapsed)
    return switches

def plot_state(h,delta):
    for flow_id in switches_by_flow:
        switches = switches_by_flow[flow_id]
        pulser = False
        last_x = 0
        for switch in switches:
            plt.plot([last_x, switch], [h-(delta/20)*flow_id, h-(delta/20)*flow_id], 'r' if pulser else 'b', linewidth=10)
            last_x = switch
            pulser = not pulser


def plot(data, col, name, xlim=None):
    plt.figure()

    # Plot Data
    plot_state(data[col].min(),data[col].max()-data[col].min())
    my_plot = sns.lineplot(x="tv_sec", y=col, data=data, hue="label", markers=True)

    # size figure etc.
    if xlim is not None:
        plt.xlim(xlim)
    fig = my_plot.get_figure()
    fig.set_size_inches(45,15)
    fig.savefig("plot-{}.png".format(name))

tcp_probe_cols = ["tv_sec", "src", "dst", "length", "snd_nxt", "snd_una", "snd_cwnd", "ssthresh", "snd_wnd", "srtt", "rcv_wnd"]


def plot_small(df, l, r):
    df = df.loc[(l <= df["tv_sec"]) & (df["tv_sec"] <= r)]

    print "Plotting cwnd for small frame..."
    plot(df, "snd_cwnd", "multiple-nimbus-cwnd-range:{},{}".format(l,r), xlim=(l,r))
    print "Plotting rtt for small frame..."
    plot(df, "srtt", "multiple-nimbus-rtt-range:{},{}".format(l,r), xlim=(l,r))

if __name__ == '__main__':
    fname = sys.argv[1]
    print "Loading data..."
    df = pd.read_csv(fname, delim_whitespace=True, header=None, names=tcp_probe_cols) 
    df["label"] = "src: " + df["src"] + ", dst: " + df["dst"]
    switches_by_flow = get_switches("nimbus/nimbus-err-1.log", 2)

    print "Plotting cwnd for all data..."
    plot(df, "snd_cwnd", "multiple-nimbus-cwnd-1")
    print "Plotting rtt for all data..."
    plot(df, "srtt", "multiple-nimbus-rtt-1")


