import socket

HOST = "127.0.0.1"
PORT = 9999

PEER_INFO = b'\x00'
PEER_INQUIRY = b'\xff'


file_list = ["peer1.py", "code.cpp"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
    peer_socket.connect((HOST, PORT))

    # sending peer_info packet
    message = " ".join(file_list).encode('utf-8')
    message_size = len(message)

    header = PEER_INFO + message_size.to_bytes(4, byteorder='big')

    peer_socket.sendall(header + message)


    while True:
        file_name = input("Enter the file u wanna download: ")

        if "exit" in file_name.lower().strip():
            break
        
        #send peer_inquiry packet
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
            peer_socket.connect((HOST, PORT))

            message = file_name.encode('utf-8')
            message_size = len(message)
            header = PEER_INQUIRY + message_size.to_bytes(4, byteorder='big')

            peer_socket.sendall(header + message)

            dest_peer = peer_socket.recv(1024) #the peer which has the file we want
            dest_peer_str = dest_peer.decode('utf-8')

            dpeer_addr = dest_peer_str.split("|")
            dpeer_ip = dpeer_addr[0]
            dpeer_port = dpeer_addr[1]

            print(dest_peer_str)