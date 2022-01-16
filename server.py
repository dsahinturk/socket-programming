import socket
from enum import Enum
from random import randint
import os
from math import ceil

HOST = '127.0.0.1'
SERVER_PORT = 65432
CLIENT_PORT = 65431
buffer_length = 1024
error_rate = 50
timeout = 0.1


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
        UDP_socket.sendto(packet, (HOST, CLIENT_PORT))


def send_and_receive_optional(UDP_socket, packet, receive=True):
    try:
        unreliable_send(UDP_socket, packet,)
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


def get_filename(data):
    return data[2:].decode("utf-8")


def is_HANDSHAKE(data):
    packet_type = data[0]
    if PacketType.HANDSHAKE.value == packet_type:
        return True


def hand_shake(UDP_socket):
    data = get_response(UDP_socket)

    # Gelen paket handshake değilse hata fırlatır
    if is_HANDSHAKE(data) is not True:
        raise Exception("Sender is not recognized!")

    # Paketten istenilen dosya ismini bulur
    print_titles("Hand Shake!")
    file_name = get_filename(data)

    # İstenilen dosya dizinde yoksa hata fırlatır
    if os.path.exists(file_name):

        # Handshake kabul etmek üzere paket hazırlanır.
        final_packet_index = ceil(os.stat(file_name).st_size / buffer_length)
        packet = bytearray([PacketType.HANDSHAKE.value, final_packet_index])
        packet.extend(bytearray(file_name, "utf-8"))

        # Socket'e bir şeylerin yolunda gitmediğini varsayacak bir timeout değeri verilir
        UDP_socket.settimeout(timeout)

        # Client'a handshake paketi yollanır
        send_and_receive_optional(UDP_socket, packet)
        return file_name
    else:
        raise Exception("File not found")


def is_ACK(data):
    packet_type = data[0]
    if PacketType.ACK.value == packet_type:
        print("ACK received for sequence number", data[1])
        return True


def send_file(UDP_socket, file_name):
    print_titles("Sending file!")

    # Dosya read ve binary mod'da açılır.
    requested_file = open(file_name, "rb")

    # Dosyanın büyüklüğü hesaplanır
    total_data_size = os.stat(file_name).st_size
    data_sent_size = 0
    sequence_number = 0

    # Gönderilen data boyutu, dosya boyutuna ulaşana kadar döngü devam eder
    while data_sent_size <= total_data_size:

        # Gönderilecek paketin ilk byte detayları doldurulur
        packet = bytearray([PacketType.DATA.value, 0, sequence_number])

        # Gönderilecek paketin içeriğine ne kadarlık data boyutu okunabileceği hesaplanır
        file_read_data_size = buffer_length - len(packet)

        # Hesaplanan boyut kadar dosya okunur
        data_read = requested_file.read(file_read_data_size)
        packet.extend(bytearray(data_read))

        # Paket gönderilir ve ack paketinin gelmesi beklenir
        received_data = send_and_receive_optional(UDP_socket, packet)
        if is_ACK(received_data) is True:

            # Ack paketi gelirse sequence numarasını bir arttırır
            sequence_number = toggle_sequence_number(sequence_number)

            # Totalde gönderilmiş dosya boyutu hesaplanır
            data_sent_size += file_read_data_size


def finish(UDP_socket):
    print_titles("Finishing!")
    sequence_number = 0

    # Fin paketi gönderilir
    packet = bytearray([PacketType.FIN.value, sequence_number])
    received_data = send_and_receive_optional(UDP_socket, packet)
    # is_ACK(received_data)
    print_titles("Finished!")


# MAIN Program
def server():
    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_socket.bind((HOST, SERVER_PORT))

    print('Connected by', UDP_socket)
    print("Waiting for requests...")
    while True:
        file_name = hand_shake(UDP_socket)

        send_file(UDP_socket, file_name)

        finish(UDP_socket)
        UDP_socket.settimeout(None)


server()
