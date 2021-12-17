from typing import NewType, Text, Tuple, NamedTuple
from threading import Thread
from socket import socket

# e.g. 127.0.0.1
IP = NewType("IP", Text)
# e.g. 5000
Port = NewType("Port", int)
# UDP addresses are uniquely identified by an IP address and
# port number
UDPAddr = NewType("UDPAddr", Tuple[IP, Port])
# Channels in Moose are threads managing full or half duplex communication
# between 2 Moost clients
Channel = NewType("Channel", Thread)


# MooseClients stream video data over UDP and perform out-of-band
# communication for Moose specific commands through a TCP connection
class MooseClient(NamedTuple):
    ip: IP
    tcp_port: Port
    udp_port: Port
    connection: socket
