import os
import re
import sys
import time
import socket
import datetime
import argparse
import termcolor
import threading

parser = argparse.ArgumentParser(
    description="Check if hosts are up.",
    formatter_class=lambda prog: argparse.HelpFormatter(
        prog, max_help_position=150, width=150
    ),
)
parser.add_argument(
    "-i",
    "--interval",
    help="The interval in minutes between checks (default 15)",
    default=5,
    type=int,
)
parser.add_argument(
    "-r",
    "--retry",
    help="The retry count when a connection fails (default 3)",
    default=3,
    type=int,
)
parser.add_argument(
    "-d",
    "--delay",
    help="The retry delay in seconds when a connection fails (default 10)",
    default=10,
    type=int,
)
parser.add_argument(
    "-t",
    "--timeout",
    help="The connection timeout in seconds (default 3)",
    default=3,
    type=int,
)
parser.add_argument(
    "-s", "--start", help="The range ips that start from 0", default=0, type=int
)
parser.add_argument(
    "-e", "--end", help="The range ips that end from 65353", default=65353, type=int
)
parser.add_argument(
    "-H",
    "--hosts",
    nargs="+",
    help="The host to monitor Format: '<server>:tcp <server>:udp' (default 127.0.0.1)",
    default=["127.0.0.1:tcp"],
)
parser.add_argument(
    "-c",
    "--connection",
    help="The connection type (default tcp) otherwise udp",
    default="tcp",
    type=str,
)

args = parser.parse_args()

ports = [
    20,
    21,
    22,
    23,
    25,
    53,
    80,
    110,
    119,
    123,
    143,
    161,
    194,
    443,
    465,
    587,
    993,
    995,
]
hosts = args.hosts
retry = args.retry
delay = args.delay
timeout = args.timeout
start = args.start
end = args.end
interval = args.interval
connection_type = args.connection


def println(string, indent, color="white"):
    strindent = ""
    for x in range(0, indent):
        strindent = strindent + " "
    print(
        termcolor.colored(
            "["
            + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + "]"
            + strindent,
            "blue",
            attrs=["bold"],
        ),
        end=" ",
    )

    print(termcolor.colored(string, color), end="")
    print()


def tcpCheck(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()


def udpCheck(ip, port):
    cmd = "nc -vzu -w " + str(timeout) + " " + ip + " " + str(port) + " 2>&1"
    res = os.popen("DATA=$(" + cmd + ");echo -n $DATA").read()
    if res != "":
        return True
    else:
        return False


def checkHost(host):
    ipup = False
    color = "white"
    for i in range(retry):
        if host["conntype"] == "udp":
            if udpCheck(host["ip"], host["port"]):
                ipup = True
                break
            else:
                println(
                    "No response from "
                    + host["ip"]
                    + ":"
                    + str(host["port"])
                    + ":"
                    + host["conntype"]
                    + ", retrying in "
                    + str(delay)
                    + "s...",
                    0,
                    color,
                )
                time.sleep(delay)
        else:
            if tcpCheck(host["ip"], host["port"]):
                ipup = True
                break
            else:
                println(
                    "No response from "
                    + host["ip"]
                    + ":"
                    + str(host["port"])
                    + ":"
                    + host["conntype"]
                    + ", retrying in "
                    + str(delay)
                    + "s...",
                    0,
                    color,
                )
                time.sleep(delay)
    return ipup


def parseHost(host):
    prestatus = host["status"]
    color = "magenta"
    println(
        "Checking "
        + host["ip"]
        + ":"
        + str(host["port"])
        + ":"
        + host["conntype"]
        + "...",
        0,
        color,
    )

    if checkHost(host):
        host["status"] = "up"
        color = "green"
        if prestatus == "down":
            changes.append(
                host["ip"]
                + ":"
                + str(host["port"])
                + ":"
                + host["conntype"]
                + " is "
                + host["status"]
            )
    else:
        host["status"] = "down"
        color = "red"
        if prestatus == "up":
            changes.append(
                host["ip"]
                + ":"
                + str(host["port"])
                + ":"
                + host["conntype"]
                + " is "
                + host["status"]
            )

    println(
        "Status of "
        + host["ip"]
        + ":"
        + str(host["port"])
        + ":"
        + host["conntype"]
        + ": "
        + host["status"],
        0,
        color,
    )


def run():
    host_list = []
    for ip in hosts:

        for port in ports:
            if port > start and port < end:
                host_list.append(
                    {
                        "ip": ip,
                        "port": port,
                        "conntype": connection_type,
                        "status": "unknown",
                    }
                )

    while True:
        threads = []
        for host in host_list:
            t = threading.Thread(target=parseHost, args=(host,))
            threads.append(t)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        del threads[:]
        println("Waiting " + str(interval) + " minutes for next check.", 0, "yellow")

        try:
            time.sleep(interval * 60)
        except:
            break


if __name__ == "__main__":
    run()