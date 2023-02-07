import socket
import sys
import os
import random
LOCAL_HOST = "127.0.0.1"
PORT = 2001
MAX_MSG_SIZE = 1024
BEGIN_SEND = "<BEGIN SEND>"
FIN = "<FIN SEND>"


def start_client(file_path):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("socket creation failed with error: " + str(e))
        return
    client_socket.connect((LOCAL_HOST, PORT))
    try:
        f = open(file_path, 'rb')
    except OSError:
        print(f"Couldn't open file: {file_path}")
        return
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    msg = f"{file_name}_{file_size}"
    client_socket.send(msg.encode())
    data = client_socket.recv(MAX_MSG_SIZE).decode()
    if data != BEGIN_SEND:
        print(data)
    else:
        handle_file(f, client_socket)

    client_socket.close()
    f.close()

def handle_file(file, client_socket):
    data = file.read()
    client_socket.sendall(data)
    client_socket.send(f"{FIN}".encode())



if __name__ == '__main__':
    if len(sys.argv) == 2:
        start_client(sys.argv[1])
