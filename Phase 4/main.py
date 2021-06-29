from os import popen
from os.path import exists
from typing import List
from struct import pack, unpack
from socket import socket, AF_PACKET, SOCK_RAW, htons, inet_aton
import argparse
import sys

import netaddr


def get_mac(interface: str = 'ens33') -> str:
    interface_path: str = f'/sys/class/net/{interface}/'
    if exists(interface_path):
        with open(f'{interface_path}address', 'r') as file:
            return file.readline().strip()
    else:
        raise FileNotFoundError("The Interface doesn't exist or was incorrect")


def arp_request(interface: str = 'ens33', dest: str = 'ff:ff:ff:ff:ff:ff', dest_ip: str = '192.168.1.102', timeout: float = 0.01) -> str:
    split_char: str = ':'

    with socket(AF_PACKET, SOCK_RAW, htons(3)) as __sock:
        __sock.bind((interface, 0))

        source_mac: bytes = pack(
            '!BBBBBB', *[int(oc, 16) for oc in get_mac(interface).split(split_char)])

        dest_mac: bytes = pack(
            '!BBBBBB', *[int(oc, 16) for oc in dest.split(split_char)])

        ethernet_header: bytes = pack('!6s6sH',
                                      dest_mac,
                                      source_mac,
                                      0x0806  # = ARP
                                      )

        source_ip = popen(
            'ip addr show '+interface+' | grep "\<inet\>" | awk \'{ print $2 }\' \
            | awk -F "/" \'{ print $1 }\'').read().strip()

        # ARP Request header, see RFC 826
        arp_header: bytes = pack('!HHBBH6s4s6s4s',
                                 0x0001,  # htype = ethernet
                                 0x0800,  # ptype = TCP
                                 0x0006,  # hardware address len
                                 0x0004,  # protocol address len
                                 0x0001,  # optype 1=request/2=reply
                                 source_mac,
                                 inet_aton(source_ip),
                                 dest_mac,
                                 inet_aton(dest_ip)
                                 )

        packet: bytes = ethernet_header + arp_header
        try:
            __sock.settimeout(timeout)
            __sock.send(packet)
            raw_data: bytes = __sock.recv(42)
            raw_data = unpack('!6s6sH HHBBH6s4s6s4s', raw_data)

            if raw_data[7] == 2:
                unpacked_data: List[int] = unpack('!BBBBBB', raw_data[8])
                unpacked_data = [f'{x:02x}' for x in unpacked_data]
                return ':'.join(unpacked_data)
        except:
            return None


parser = argparse.ArgumentParser(prog="arp")
parser.add_argument('-s', '--start', dest="start_ip_addr",
                    type=str, metavar="START_IP_ADDR")
parser.add_argument('-e', '--end', dest="end_ip_addr",
                    type=str, metavar="END_IP_ADDR")
parser.add_argument('-r', '--range', dest="ip_range",
                    metavar="IP_RANGE", nargs="*")
parser.add_argument("-w", "--wait", dest="timeout", metavar="TIMEOUT", type=float, default=0.01,
                    help="Default  4.")
parser.add_argument("-i", "--interface", dest="interface",
                    metavar="INTERFACE", default="", help="LINUX ONLY.")
args = parser.parse_args(sys.argv[1:])

if args.ip_range is not None:
    netID = args.ip_range[0]
    net_range = [str(ip) for ip in list(netaddr.IPNetwork(netID))]
elif args.start_ip_addr is not None and args.end_ip_addr is not None:
    net_range = [args.start_ip_addr[:-3] + str(i) for i in range(
        int(args.start_ip_addr[-3:]), int(args.end_ip_addr[-3:]))]
else:
    print("Wrong Input")
    sys.exit()

for ip in net_range:
    host_status = arp_request(interface=args.interface,
                              dest_ip=ip, timeout=args.timeout)
    if host_status is not None:
        print("Host {ip} Is Up\nMac Address = ".format(ip=ip)+host_status)
