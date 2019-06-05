#!/usr/bin/python2
import matplotlib
matplotlib.use('tkagg')

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re, sys

def get_elasticity_data_from_nimbus_log(fname, filter_master=True, ids_to_labels={}):
    data = []
    with open(fname) as f:
        start = None
        for l in f.readlines():
            if "elasticity_inf" in l:
                flow_id = int(re.search(r"ID: (\d+)", l).group(1))
                if filter_master and flow_id == 1:
                    continue
                if flow_id in ids_to_labels:
                    flow_id = ids_to_labels[flow_id]

                elapsed = float(re.search(r"elapsed: ([\d\.]+)", l).group(1))
                elasticity = float(re.search(r"EWMAElasticity: ([\d\.]+)", l).group(1))
                data.append([flow_id, elapsed, elasticity])
                
    df = pd.DataFrame(data, columns=['id', 'elapsed', 'peak(4.5,6.5) / peak(7,13)'])

    return df

def get_rate_data_from_nimbus_log(fname, ids_to_labels={}):
    data = []
    with open(fname) as f:
        start = None
        for l in f.readlines():
            if "got ack" in l:
                flow_id = int(re.search(r"ID: (\d+)", l).group(1))
                if flow_id in ids_to_labels:
                    flow_id = ids_to_labels[flow_id]
                elapsed = float(re.search(r"elapsed: ([\d\.]+)", l).group(1))
                rin = float(re.search(r"rin: ([\d\.]+)", l).group(1))
                rout = float(re.search(r"rout: ([\d\.]+)", l).group(1))
                rtt = float(re.search(r" rtt: ([\d\.]+)", l).group(1))
                curr_cwnd = float(re.search(r"curr_cwnd: ([\d\.]+)", l).group(1))
                curr_rate = float(re.search(r"curr_rate: ([\d\.]+)", l).group(1))
                data.append([flow_id, elapsed, rin, rout, rtt, curr_cwnd, curr_rate])
                
    df = pd.DataFrame(data, columns=['id', 'elapsed', 'rin', 'rout', 'rtt', 'curr_cwnd', 'curr_rate'])

    return df

def plot(data, col, name=None, custom_y_label=None):
    plt.figure()

    # Plot Data
    fig, ax = plt.subplots()
    my_plot = sns.lineplot(x="elapsed", y=col, data=data, hue="id", markers=True, ax=ax, legend="full")

    # print("Plotting elasticity data...")
    # ax2 = ax.twinx()
    # my_plot = sns.lineplot(x="elapsed", y="rin", data=data, hue="id", markers=False, ax=ax2)
    # my_plot = sns.lineplot(x="elapsed", y="rout", data=data, hue="id", markers=False, ax=ax2)

    if name != None:
        fig.savefig("plot-{}.png".format(name))
    else:
        fig.show()



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Need filename of nimbus output"
        sys.exit(1)

    fname = sys.argv[1]

    # ids_to_labels = {1: "Pulser (Bottleneck 1)", 2:"Watcher 1 (Bottleneck 1)", 3:"Watcher 2 (Bottleneck 2)", 4: "Watcher 3 (Bottleneck 2)"}
    df_elasticity = get_elasticity_data_from_nimbus_log(fname)
    df_rate = get_rate_data_from_nimbus_log(fname)
    plot(df_elasticity, "peak(4.5,6.5) / peak(7,13)")
    plot(df_rate, "rtt")
    plot(df_rate, "rin")
    print("Done! Type 'q' to finish viewing...")

    while True:
        if (sys.version_info > (3, 0)):
            x = input("")
        else:
            x = raw_input("")
        if x == "q":
            print("Closing session...")
            break
