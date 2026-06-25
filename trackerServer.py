import socket

BUFFER = 4096
HOST = "127.0.0.1"
PORT = 9999

peer_list = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    peer_conn, peer_addr = server_socket.accept()

    with peer_conn:
        
        header = peer_conn.recv(4)
        message = b""

        message_size = int.from_bytes(header, byteorder='big')

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

        peer_info = f"{peer_addr[0]}|{str(peer_addr[1])}|{message_str}"
        peer_list.append(peer_info)
        print(peer_list)