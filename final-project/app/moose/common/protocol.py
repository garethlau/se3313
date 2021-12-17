from .types import IP, Port

terminate_client = "EXIT"
terminate_server = "KILL"


def notify_client_connection_created(ip: IP, udp_port: Port):
    return f"CONNECTION CREATED WITH: ('{ip}', {udp_port})"


def request_session_from_server(client_udp_port: Port):
    return f"CONNECT UDP: {client_udp_port}"
