import socket
import threading
import os

BUFFER = 4096

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

PEER_IP = "0.0.0.0"
PEER_LPORT = 37000

PEER_INFO = b'\x00'
PEER_INQUIRY = b'\xff'
FILE_DOWNLOAD = b'\xaa'
FILE_CONTENT = b'\x77'

def recieve_data(peer_conn, message_size):
    message = b""
    temp_msg_size = message_size
    recv_size = BUFFER
    while True:
        if temp_msg_size <= min(temp_msg_size, BUFFER):
            message_frag = peer_conn.recv(temp_msg_size)
            recv_size = len(message_frag)
            message += message_frag

            if recv_size < temp_msg_size:
                temp_msg_size -= recv_size
                continue

            break
            
        message_frag = peer_conn.recv(BUFFER)
        recv_size = len(message_frag)
        message += message_frag
        temp_msg_size -= recv_size

    return message.decode('utf-8')

def peer_listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
        peer_socket.bind((PEER_IP, PEER_LPORT))
        peer_socket.listen()

        #node refers to other peers that are trying to connect with this peer
        node_conn, node_addr = peer_socket.accept()

        #get the file name and then send the file
        packet_status = node_conn.recv(1)

        if packet_status != FILE_DOWNLOAD:
            return
        
        msg_size = node_conn.recv(4)
        file_name = recieve_data(node_conn, msg_size)

        file_size = os.path.getsize(file_name)
        header = FILE_CONTENT + file_size.to_bytes(4, byteorder='big')

        with open(file_name, 'rb') as f:
            if file_size < BUFFER:
                peer_socket.sendall(header + f.read())

            else:
                temp_file_size = file_size - BUFFER
                chunk = f.read(BUFFER)
                peer_socket.sendall(header)
                peer_socket.sendall(chunk)
                while True:
                    if temp_file_size < BUFFER:
                        peer_socket.sendall(f.read())
                        break

                    chunk = f.read(BUFFER)
                    peer_socket.sendall(chunk)
                    temp_file_size -= BUFFER




file_list = ["peer2.py", "code.cpp"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
    peer_socket.connect((SERVER_IP, SERVER_PORT))

    # sending peer_info packet
    message = " ".join(file_list).encode('utf-8')
    message = f"{str(PEER_LPORT)}|{message}"
    message_size = len(message)

    header = PEER_INFO + message_size.to_bytes(4, byteorder='big')

    peer_socket.sendall(header + message)

#after initial setup the peer should listen for reqs as well so createing a thread for that
listening_thread = threading.Thread(target=peer_listen)
listening_thread.start()


while True:
    command = input("$ ")
    formatted_command = command.lower().strip()

    if "exit" in formatted_command:
        break

    elif "download" in formatted_command:
        file_name = formatted_command.split(" ")[1]


    #send peer_inquiry packet
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
        peer_socket.connect((SERVER_IP, SERVER_PORT))


        message = file_name.encode('utf-8')
        message_size = len(message)
        header = PEER_INQUIRY + message_size.to_bytes(4, byteorder='big')
        peer_socket.sendall(header + message)

        packet_status = peer_socket.recv(1)
        message_length = peer_socket.recv(4)
        message_size = int.from_bytes(message_length, byteorder='big')

        dest_peer_str =""
        if packet_status == PEER_INFO:
            dest_peer_str = recieve_data(peer_socket, message_size) #the peer which has the file we want

        dpeer_addr = dest_peer_str.split("|")
        dpeer_ip = dpeer_addr[0]
        dpeer_port = int(dpeer_addr[1])

        print(dpeer_ip)
        print(dpeer_port)

    #downloading the file
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
        peer_socket.connect((dpeer_ip, dpeer_port))

        #header containing the name of file to be downloaded
        message = file_name.encode('utf-8')
        message_size = len(message)
        header = FILE_DOWNLOAD + message_size.to_bytes(4, byteorder='big')
        peer_socket.sendall(header + message)  

        packet_status = peer_socket.recv(1)

        if packet_status == FILE_CONTENT:
            file_size = int.from_bytes(peer_socket.recv(4), byteorder='big')
            
            #create and save the file
            with open(file_name, 'wb') as f:
                temp_file_size = file_size
                recv_size = BUFFER
                while True:
                    if temp_file_size <= min(temp_file_size, BUFFER):
                        file_frag = peer_socket.recv(temp_file_size)
                        recv_size = len(file_frag)
                        f.write(file_frag)

                        if recv_size < temp_file_size:
                            temp_file_size -= recv_size
                            continue

                        break
                        
                    file_frag = peer_socket.recv(BUFFER)
                    recv_size = len(file_frag)
                    f.write(file_frag)
                    temp_file_size -= recv_size
        