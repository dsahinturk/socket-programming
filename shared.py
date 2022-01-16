from enum import Enum
from random import randint

HOST = '127.0.0.1'
SERVER_PORT = 65432
CLIENT_PORT = 65431
buffer_length = 1024
file_name = "crime-and-punishment.txt"


class PacketType(Enum):
    HANDSHAKE = 0
    ACK = 1
    DATA = 2
    FIN = 3


def get_response(UDP_socket):
    data, ip_port = UDP_socket.recvfrom(1024)
    print("Received:", data)
    return data


def unreliable_send(UDP_socket, PORT, packet, error_rate=0):
    print("Sending:", packet)
    if error_rate < randint(0, 100):
        UDP_socket.sendto(packet, (HOST, PORT))


def send_and_receive_optional(UDP_socket, PORT, packet, error_rate=0, receive=True):
    try:
        unreliable_send(UDP_socket, PORT, packet, error_rate)
        if receive is True:
            packet_received = get_response(UDP_socket)
            return packet_received
    except:
        print("Timeout")
        return send_and_receive_optional(UDP_socket, PORT, packet, error_rate, receive)


def toggle_sequence_number(sequence_number):
    if sequence_number == 1:
        return 0
    if sequence_number == 0:
        return 1


def print_titles(text):
    print()
    print(text)
    print()
