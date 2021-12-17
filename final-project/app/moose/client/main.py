import fire
import errno
import threading
from cv2 import cv2
import socket
import pickle
import time
import ast
from ..common import types as mt
from ..common import config
from ..common import protocol

udp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 100000)

tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

is_capturing = True
should_graceful_exit = False


def tcp_listen():
    global should_graceful_exit
    while True:
        try:
            msg = tcp_s.recv(1024)
        except socket.error as e:
            if e.errno == config.EBADFD:
                break
            else:
                raise e

        if msg.decode() == protocol.terminate_server:
            # The server has terminated
            print("The server is terminating. The client will now terminate.")
            break
        elif msg.decode() == protocol.terminate_client:
            # This clients session partner has quit Moose
            print("Your session has terminated. The client will now terminate.")
            break
        else:
            print("Invalid message received from server.")
    should_graceful_exit = True


def capture(sendto_addr: mt.UDPAddr):
    global is_capturing
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera.")
        exit()
    while is_capturing:
        # time.sleep(0.005)
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Compress frame as JPG
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
        x_as_bytes = pickle.dumps(buffer)
        udp_s.sendto(x_as_bytes, sendto_addr)

    cap.release()


def manage_session(
    server_ip: mt.IP = config.DEFAULT_SERVER_IP,
    server_port: mt.Port = config.DEFAULT_SERVER_PORT,
    base_read_port: mt.Port = config.CLIENT_BASE_READ_PORT,
):
    global is_capturing
    global should_graceful_exit

    # Discover and bind to unused read port
    read_port = base_read_port
    while True:
        try:
            # Listen on all incoming traffic
            udp_s.bind(("0.0.0.0", read_port))
            break
        except socket.error as e:
            # PORT is in use, try the next PORT number
            read_port += 1

    tcp_s.connect((server_ip, server_port))
    tcp_s.send(bytes(protocol.request_session_from_server(read_port), "utf-8"))
    # Client will wait until receipt of notify_client_connection_created message
    # from the server.
    # e.g. "CONNECTION CREATED WITH: ('127.0.0.1', 3000)"
    msg = tcp_s.recv(1024)
    sendto_addr = mt.UDPAddr(
        ast.literal_eval(msg.decode("utf-8").split(":")[1].strip())
    )

    # Create and start thread to capture video data and send to server
    capture_thread = threading.Thread(target=capture, args=[sendto_addr])
    capture_thread.start()

    # Create and start a thread to listen to TCP data from server
    listen_thread = threading.Thread(target=tcp_listen)
    listen_thread.start()

    while not should_graceful_exit:
        bytestream, _ = udp_s.recvfrom(100000)

        data = pickle.loads(bytestream)

        # Decode received jpg image
        image_frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

        # Show the recived image frame
        cv2.imshow("Moose Session", cv2.resize(image_frame, (300, 200)))

        # Wait for render
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    # Gracefully exit
    tcp_s.send(bytes(protocol.terminate_client, "utf-8"))
    is_capturing = False
    capture_thread.join()
    listen_thread.join()
    udp_s.close()
    tcp_s.close()
    cv2.destroyAllWindows()


def main():
    fire.Fire(manage_session)


if __name__ == "__main__":
    main()
