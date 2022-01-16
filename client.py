import socket
from enum import Enum
from random import randint

HOST = '127.0.0.1'
SERVER_PORT = 65432
CLIENT_PORT = 65431
buffer_length = 1024
file_name = "crime-and-punishment.txt"
timeout = 1
# Sadece serverdaki error rate 0'dan büyük olursa doğru şekilde çalışıyor. Client'ın da paketlerinin kaybolması
# senaryosunu yapamadım.
error_rate = 0


class PacketType(Enum):
    HANDSHAKE = 0
    ACK = 1
    DATA = 2
    FIN = 3


def get_response(UDP_socket):
    data, ip_port = UDP_socket.recvfrom(1024)
    print("Received:", data)
    return data


def unreliable_send(UDP_socket, packet):
    print("Sending:", packet)
    if error_rate < randint(0, 100):
        UDP_socket.sendto(packet, (HOST, SERVER_PORT))


def send_and_receive_optional(UDP_socket, packet, receive=True):
    try:
        unreliable_send(UDP_socket, packet)
        if receive is True:
            packet_received = get_response(UDP_socket)
            return packet_received
    except:
        print("Timeout")
        return send_and_receive_optional(UDP_socket, packet, receive)


def toggle_sequence_number(sequence_number):
    if sequence_number == 1:
        return 0
    if sequence_number == 0:
        return 1


def print_titles(text):
    print()
    print(text)
    print()



def hand_shake(UDP_socket):
    print_titles("Hand Shake!")

    # Handshake paketi oluşturulur.
    packet = bytearray([PacketType.HANDSHAKE.value, len(file_name)])
    packet.extend(bytearray(file_name, "utf-8"))

    # Handshake paketi gönderilir.
    packet_received = send_and_receive_optional(UDP_socket, packet)

    # Ack paketi gönderilir.
    send_ACK(UDP_socket)
    return packet_received


def send_ACK(UDP_socket, sequenceNumber=0):
    packet = bytearray([PacketType.ACK.value, sequenceNumber])
    send_and_receive_optional(UDP_socket, packet, receive=False)


def is_FIN(data):
    packet_type = data[0]
    if PacketType.FIN.value == packet_type:
        print("FIN received")
        return True


def receive_file(UDP_socket):
    print_titles("Receiving file: " + file_name)
    sequence_number = None
    while True:

        # Gelen paket okunur
        packet_received = get_response(UDP_socket)

        # Paket tipi FIN ise receive file metodundan çıkar
        if is_FIN(packet_received) is True:
            break
        received_sequence_number = packet_received[2]
        sequence_number = received_sequence_number

        # Ack paketi gönderilir
        send_ACK(UDP_socket, sequence_number)

    return packet_received


def finish(UDP_socket, packet):
    print_titles("Finishing!")
    sequence_number = packet[1]
    sequence_number = toggle_sequence_number(sequence_number)
    send_ACK(UDP_socket, sequence_number)


# MAIN Program
def client():
    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_socket.bind((HOST, CLIENT_PORT))
    print('Connected by', UDP_socket)

    hand_shake(UDP_socket)

    packet = receive_file(UDP_socket)

    finish(UDP_socket, packet)
    print_titles("Closing!")
    UDP_socket.close()


client()
