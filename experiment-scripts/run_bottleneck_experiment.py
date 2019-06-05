import sys, os
import subprocess as sh
from time import sleep
import argparse


# Argparse
def parse_bottlenecks_arg(s):
    out = map(lambda x: x.split(","), s.split(";"))
    return list(out)

parser = argparse.ArgumentParser(description='run bottleneck detector experiment')
parser.add_argument('duration', metavar='T', type=int, default=60)
parser.add_argument('experiment_description', metavar='desc', type=str, default="")
parser.add_argument('bottlenecks', type=parse_bottlenecks_arg, default="", help="semicolon separated list of bottleneck args in the form: num_flows,num_cross_traffic")


# Globals
running_processes = []

# Constants
nimbus_path = "/home/ubuntu/nimbus/target/debug/nimbus"
log_folder = "/home/ubuntu/bottleneck-detection/results/logs"
mm_file = "/home/ubuntu/bottleneck-detection/experiment-scripts/48Mbps"

def call(args, stderr=None, stdout=None):
    if stderr is None:
        stderr = sh.DEVNULL
    if stdout is None:
        stdout = sh.DEVNULL

    print(">", " ".join(args))
    p = sh.Popen(args, stderr=stderr, stdout=stdout)
    running_processes.append(p)
    return p

def run_nimbus(outfile):
    args = ['sudo', nimbus_path, '--ipc=netlink', '--use_switching=false', '--flow_mode=XTCP', '--bw_est_mode=false', '--uest=48']
    return call(args, stderr=outfile)

def run_iperf_server(p=5001):
    args = ["iperf", "-s", "-p", str(p)]
    return call(args)

def mm_shell(prog):
    mm_delay = 'mm-delay 25'
    mm_link = 'mm-link --uplink-queue="droptail" --uplink-queue-args="packets=400"  --downlink-queue-args="packets=400" --downlink-queue="droptail" {} {}'.format(mm_file, mm_file)
    mm_command = ' '.join([mm_delay, mm_link, prog])
    print(">", mm_command)
    return sh.Popen(mm_command, shell=True)

def iperf_clients_in_mm_shell(num_flows, num_cross_traffic, duration):
    return mm_shell("./iperf-clients.sh {} {} {}".format(num_flows, num_cross_traffic, duration))

def pkill(procnames):
    if not isinstance(procnames, list):
        procnames = [procnames]
    for procname in procnames:
        proc = sh.Popen("sudo pkill -9 -e {}".format(procname),
                shell=True)
        proc.wait()

if __name__ == "__main__":
    args = parser.parse_args()

    pkill(["iperf", "nimbus"])

    fname = "{}/nimbus-{}.log".format(log_folder, args.experiment_description)
    print("Starting nimbus. Storing log at {}".format(fname))
    nimbus_log = open(fname,"w")
    run_nimbus(nimbus_log)
    run_iperf_server()
    sleep(0.2)

    for bottleneck in args.bottlenecks:
        num_flows = bottleneck[0]
        num_cross_traffic = bottleneck[1]
        iperf_clients_in_mm_shell(num_flows, num_cross_traffic, args.duration)

    sleep(args.duration + 5)