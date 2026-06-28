import socket
import threading

BUFFER = 4096
HOST = "127.0.0.1"
PORT = 9999

PEER_INFO = b'\x00'
PEER_INQUIRY = b'\xff'

peer_list = []

def peer_thread_function(peer_conn, peer_addr):
    with peer_conn:
        packet_status = peer_conn.recv(1)
        print(packet_status)
        message_length = peer_conn.recv(4)
        message = b""

        message_size = int.from_bytes(message_length, byteorder='big')

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

        message_str = message.decode('utf-8')

        if packet_status == PEER_INFO:
            peer_info = f"{peer_addr[0]}|{str(peer_addr[1])}|{message_str}"

            lock = threading.Lock()
            
            with lock:
                peer_list.append(peer_info)
                print(peer_list)

        if packet_status == PEER_INQUIRY:
            #iterate thorough peer list
            for i in range(len(peer_list)):
                peer_data = peer_list[i].split("|")
                file_list = peer_data[2].split(" ")

                results = [(peer_data[0], peer_data[1]) for item in file_list if item == message_str]

                if results:
                    dpeer_ip, dpeer_port = results[0]
            
            dpeer_details = f"{dpeer_ip}|{dpeer_port}"
            peer_conn.sendall(dpeer_details.encode('utf-8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    while True:
        peer_conn, peer_addr = server_socket.accept()

        peer_thread = threading.Thread(target=peer_thread_function, args=(peer_conn, peer_addr))
        peer_thread.start()
    