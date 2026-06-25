import socket

HOST = "127.0.0.1"
PORT = 9999

file_list = ["name.py", "code.cpp"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
    peer_socket.connect((HOST, PORT))
    message = " ".join(file_list).encode('utf-8')
    message_size = len(message)

    header = message_size.to_bytes(4, byteorder='big')

    peer_socket.sendall(header + message)
