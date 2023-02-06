import threading
import sys
import socket
import os

LOCAL_HOST = "127.0.0.1"
CUR_THREADS = 0
MAX_QUEUE = 5
PORT = 2001
MAX_MSG_SIZE = 1024
thread_mutex = threading.Lock()
FILE_EXTENSIONS = {".PNG", ".jpg", ".txt"}
OVERLOADED_MSG = "Server is overloaded, try again later..."
INVALID_EXTENSION = "Didn't receive correct file type"
BEGIN_SEND = "<BEGIN SEND>"
FIN = "<FIN SEND>"

def check_input():
    if len(sys.argv) != 2:
        print("didn't get thread pool size")
        return False
    try:
        thread_pool = int(sys.argv[1])
    except ValueError:
        print("thread pool is not a number, please enter a number between 5-20")
        return False
    if thread_pool < 5 or thread_pool > 20:
        print("thread pool must be a number between 5-20")
        return False
    return thread_pool

def start_server(thread_pool):
    try:
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("socket creation failed with error: " + str(e))
        return
    listen_socket.bind((LOCAL_HOST, PORT))
    listen_socket.listen(MAX_QUEUE)
    global CUR_THREADS
    # TODO: what to do if max threads are active but getting new connections?
    while True:
        print("Server listening...")
        client, addr = listen_socket.accept()
        thread_mutex.acquire()
        if CUR_THREADS < thread_pool:
            t = threading.Thread(target=handle_client, args=(client, addr))
            CUR_THREADS += 1
            thread_mutex.release()
            t.start()
        else:
            client.send(OVERLOADED_MSG.encode())
            client.close()


def handle_client(client, addr):
    print(f"got connection from: {addr}")
    global CUR_THREADS
    data = client.recv(MAX_MSG_SIZE).decode()
    file_name, file_size = data.rsplit('_', 1)
    file_name, file_extension = os.path.splitext(file_name)
    if file_extension not in FILE_EXTENSIONS:
        client.send(INVALID_EXTENSION.encode())
    else:
        client.send(BEGIN_SEND.encode())
        handle_file(client, file_name, int(file_size))
        thread_mutex.acquire()
        CUR_THREADS -= 1
        thread_mutex.release()
    client.close()

def handle_file(client, file_name, file_size):
    rand = client.recv(MAX_MSG_SIZE).decode()
    print(f"Server got {rand}")
    file_bytes = get_client_file(client, rand, file_size)
    file = open(file_name+".txt", "wb")
    file.write(file_bytes)
    file.close()
def get_client_file(client, rand, file_size):
    file_bytes = b""
    fin_msg = f"{FIN}_{rand}".encode()
    fin_len = len(fin_msg)
    while True:
        data = client.recv(MAX_MSG_SIZE)
        file_bytes += data
        if file_bytes[-fin_len:] == fin_msg:
            print(f"file size {file_size}")
            file_bytes = file_bytes[:file_size]
            print(f"file bytes len {len(file_bytes)}")
            break
    return file_bytes

def send_file_to_client(client):
    pass

if __name__ == '__main__':
    thread_pool = check_input()
    if thread_pool:
        start_server(thread_pool)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
