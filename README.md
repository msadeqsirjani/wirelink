# WIRELINK

WIRELINK is a cli application written in PYTHON for utilizing network monitoring. It can sniff ports and packets, ping multiple hosts simultaneously and traceroute any host! It supports IPV4 ping and tracerouting.

## Abilities

### Port sniffer

Currently we support multi thread port sniffing with different levels of verbosity, in near future we will add range filter support.

### Packet sniffer

At the moment there are plenty protocols that we support :

* Ethernet
* IPv4
* Arp (Address Resolution Protocol)
* Tcp (TLS, encrypted and plaintext)
* Udp (DNS queries and answers)
* There is an option for you too see a list containing all your interfaces.

You can capture packages from all of your interfaces, even bus, Dbus and bluetooth, but non network-related interfaces will not be parsed but still you can review raw payload and length of packet and time stamps.

### Ping

Unlike other ping implementations it can ping multiple hosts simultaneously, Also it tries to find ipv6 address of any host and if that exists skywalker will ping that too.

### Traceroute

You can almost set every possible variable for tracerouting using this tool, including protocol used for route tracing and packet size.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
