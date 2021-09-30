from os import popen
from os.path import exists
from typing import List
from struct import pack, unpack
from socket import socket, AF_PACKET, SOCK_RAW, htons
import argparse
import sys

import netaddr


class Arp:
    interface = None
    destination = None
    destination_ip = None
    timeout = None

    def __init__(self, interface='ends33', destination='ff:ff:ff:ff:ff:ff', destination_ip='192.168.1.102', timeout=0.01):
        self.interface = interface
        self.destination = destination
        self.destination_ip = destination_ip
        self.timeout = timeout

    def mac_address(self, interface: str) -> str:
        if str is None:
            interface = 'ens33'
        interface_path: str = f'/sys/class/net/{interface}/'
        if exists(interface_path):
            with open(f'{interface_path}address', 'r') as file:
                return file.readline().strip()
        else:
            print("The interface doesn't exist or was incorrect")
            sys.exit()

    def start_arp_request(self, timeout: float = 0.01) -> str:
        spliter: str = ':'

        with socket(AF_PACKET, SOCK_RAW, htons(3)) as request:
            request.bind((self.interface, 0))

            source_mac_address: bytes = pack(
                '!BBBBBB', *[int(oc, 16) for oc in mac_address(self.interface).split(spliter)])

            destination_mac_address: bytes = pack(
                '!BBBBBB', *[int(oc, 16) for oc in self.destination.split(spliter)])

            ethernet_header: bytes = pack(
                '!6s6sH', destination_mac_address, source_mac_address, 0x0806)

            source_ip = popen('ip addr show ' + self.interface +
                              ' | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()

            arp_header: bytes = pack('!HHBBH6s4s6s4s',
                                     0x0001,  # htype = ethernet
                                     0x0800,  # ptype = TCP
                                     0x0006,  # hardware address len
                                     0x0004,  # protocol address len
                                     0x0001,  # optype 1=request/2=reply
                                     source_mac_address,
                                     socket.inet_aton(source_ip),
                                     destination_mac_address,
                                     socket.inet_aton(self.destination_ip))

            packet: bytes = ethernet_header + arp_header

            try:
                request.settimeout(timeout)
                request.send(packet)
                raw_data: bytes = request.recv(42)
                raw_data = unpack('!6s6sH HHBBH6s4s6s4s', raw_data)

                unpacked_data: List[int] = unpack('!BBBBBB', raw_data[8])    
                unpacked_data = [hex(x) for x in unpacked_data]
                return ':'.join(unpacked_data)
            except:
                return None


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', required=False,
                        nargs='?', type=str, metavar="starting ip address")
    parser.add_argument('-e', '--end', required=False, nargs='?',
                        type=str, metavar="ending ip address")
    parser.add_argument('-r', '--ip_range', required=False, nargs='*',
                        metavar="ip range")
    parser.add_argument("-w", "--wait", required=False, nargs='?', metavar="timeout",
                        type=float, default=0.01)
    parser.add_argument("-i", "--interface", metavar="interface", default="", help="LINUX ONLY.")

    return parser


def arp_request(ip_range, start, end, timeout, interface):
    if ip_range is not None:
        netID = ip_range
        net_range = [str(ip) for ip in list(netaddr.IPNetwork(netID))]
    elif start is not None and end is not None:
        net_range = [start[:-3] + str(i) for i in range(
            int(start[-3:]), int(end[-3:]))]
    else:
        print("input is wrong")
        sys.exit()

    for ip in net_range:
        host_status = Arp(interface=interface,
                          destination_ip=ip, timeout=timeout)
        if host_status is not None:
            print("Host {ip} is up | mac address = ".format(
                ip=ip) + host_status.start_arp_request(timeout=timeout))


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    ip_range = args.ip_range
    start = args.start
    end = args.end
    wait = args.wait
    interface = args.inteface

    arp_request(ip_range, start, end, wait, interface)
