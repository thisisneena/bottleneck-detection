import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

def get_switches(fname):
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

def get_ewma_elasticity(fname, time_shift=0, filter_master=True):
    data = []
    with open(fname) as f:
        start = None
        for l in f.readlines():
            if "EWMAElasticity" in l:
                flow_id = int(re.search(r"ID: (\d+)", l).group(1))
                elapsed = float(re.search(r"elapsed: ([\d\.]+)", l).group(1))
                elasticity = float(re.search(r"EWMAElasticity: ([\d\.]+)", l).group(1))
                data.append([flow_id, time_shift+elapsed, elasticity])
    df = pd.DataFrame(data, columns=['id', 'elapsed', 'elasticity'])
    if filter_master:
        df = df[df["id"] != 1]
    return df


def plot_state(switches_by_flow, data, col):
    min_y, max_y, min_x, max_x = data[col].min(), data[col].max(), data["tv_sec"].min(), data["tv_sec"].max()
    h = min_y 
    delta_y = max_y - min_y

    for flow_id in switches_by_flow:
        switches = switches_by_flow[flow_id]
        switches.append(max_x-min_x)
        pulser = False
        last_x = 0
        for switch in switches:
            plt.plot([min_x + last_x, min_x + switch], [h-(delta_y/20)*flow_id, h-(delta_y/20)*flow_id], 'r' if pulser else 'b', linewidth=10)
            last_x = switch
            pulser = not pulser


def plot(data, switches, col, name=None, xlim=None, elasticity_data=None):
    plt.figure()

    # Plot Data
    fig, ax = plt.subplots()
    plot_state(switches, data, col)
    my_plot = sns.lineplot(x="tv_sec", y=col, data=data, hue="label", markers=True, ax=ax)

    if elasticity_data is not None:
        ax2 = ax.twinx()
        print("Plotting elasticity data...")
        my_plot = sns.lineplot(x="elapsed", y="elasticity", data=elasticity_data, hue="id", markers=False, ax=ax2)

    # size figure etc.
    if xlim is not None:
        plt.xlim(xlim)

    if name != None:
        fig.savefig("plot-{}.png".format(name))
    else:
        fig.show()


def plot_small(df, l, r):
    df = df.loc[(l <= df["tv_sec"]) & (df["tv_sec"] <= r)]

    # print "Plotting cwnd for small frame..."
    plot(df, "snd_cwnd", "multiple-nimbus-cwnd-range:{},{}".format(l,r), xlim=(l,r))
    # print "Plotting rtt for small frame..."
    plot(df, "srtt", "multiple-nimbus-rtt-range:{},{}".format(l,r), xlim=(l,r))

tcp_probe_cols = ["tv_sec", "src", "dst", "length", "snd_nxt", "snd_una", "snd_cwnd", "ssthresh", "snd_wnd", "srtt", "rcv_wnd"]
def import_tcp_probe_data(fname, filter_acks=True):
    df = pd.read_csv(fname, delim_whitespace=True, header=None, names=tcp_probe_cols) 
    df["label"] = "src: " + df["src"] + ", dst: " + df["dst"]

    if filter_acks:
        df = df[~df["src"].str.contains(":5001")]

    return df