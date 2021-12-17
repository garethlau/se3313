from typing import List, Optional
import socket
import pickle
import numpy
import threading
import errno
import time
from ..common import types as mt
from ..common import config
from ..common import protocol


tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Listen on all incoming traffic
tcp_s.bind(("0.0.0.0", config.DEFAULT_SERVER_PORT))
tcp_s.listen()

is_creating_channels = True
is_channels_open = True

active_connections: List[socket.socket] = []


def tcp_half_duplex(listen_connection: socket.socket, write_connection: socket.socket):
    global is_channels_open
    while is_channels_open:
        try:
            msg = listen_connection.recv(1024)
            if msg.decode() == protocol.terminate_client:
                # Forward client termination message to other client
                write_connection.send(msg)
                break
        except socket.error as e:
            if e.errno == config.EBADFD:
                print("Half duplex communication channel is closed.")
                break
            else:
                raise e


def tcp_full_duplex(connection_one: socket.socket, connection_two: socket.socket):
    c_one_listen = threading.Thread(
        target=tcp_half_duplex, args=[connection_one, connection_two]
    )
    c_two_listen = threading.Thread(
        target=tcp_half_duplex, args=[connection_two, connection_one]
    )
    c_one_listen.start()
    c_two_listen.start()
    c_one_listen.join()
    c_two_listen.join()


def create_channels():
    global is_channels_open
    global active_connections
    prev_client: Optional[mt.MooseClient] = None
    channels: List[mt.Channel] = []

    while is_creating_channels:
        try:
            connection, tcp_client = tcp_s.accept()
            print("Creating connection ", tcp_client)
        except ConnectionAbortedError:
            break

        data = connection.recv(1024)
        client_udp_port = mt.Port(int(data.decode("utf-8").split(":")[1].strip()))
        client = mt.MooseClient(
            tcp_client[0], tcp_client[1], client_udp_port, connection
        )

        # This is the first client for a new transaction
        if prev_client is None:
            prev_client = client
            continue

        # Notify the first client who it should connect with
        prev_client.connection.send(
            bytes(
                protocol.notify_client_connection_created(client.ip, client.udp_port),
                "utf-8",
            )
        )
        # Notify the second client who it should connect with
        client.connection.send(
            bytes(
                protocol.notify_client_connection_created(
                    prev_client.ip, prev_client.udp_port
                ),
                "utf-8",
            )
        )

        # Making a new transaction with the prev and new client
        channel = threading.Thread(
            target=tcp_full_duplex, args=[prev_client.connection, client.connection]
        )
        channel.start()
        channels.append(channel)

        active_connections.append(prev_client.connection)
        active_connections.append(client.connection)

        prev_client = None

    is_channels_open = False
    for channel in channels:
        channel.join()


def main():
    global active_connections
    global is_creating_channels
    creating_thread = threading.Thread(target=create_channels)
    creating_thread.start()
    while True:
        data = input("Type q to gracefully quit the server\n")
        if data == "q":
            break

    is_creating_channels = False

    for active_connection in active_connections:
        active_connection.send(protocol.terminate_server.encode())
        active_connection.close()

    tcp_s.close()
    creating_thread.join()


if __name__ == "__main__":
    main()
