import threading
import sys
import socket
import os
import cv2
import numpy as np

LOCAL_HOST = "127.0.0.1"
CUR_THREADS = 0
MAX_QUEUE = 5
PORT = 2001
MAX_MSG_SIZE = 1024
thread_mutex = threading.Lock()
MAX_POOL = 20
MIN_POOL = 5
IMG_EXTENSIONS = {".PNG", ".jpg"}
VID_EXTENSIONS = {".mov", ".mp4"}
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
    if thread_pool < MIN_POOL or thread_pool > MAX_POOL:
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
            print(CUR_THREADS)
            t.start()
        else:
            client.send(OVERLOADED_MSG.encode())
            client.close()
        thread_mutex.release()


def handle_client(client, addr):
    print(f"got connection from: {addr}")
    global CUR_THREADS
    data = client.recv(MAX_MSG_SIZE).decode()
    file_name, file_size = data.rsplit('_', 1)
    file_name, file_extension = os.path.splitext(file_name)
    print(file_extension)
    if file_extension in IMG_EXTENSIONS or file_extension in VID_EXTENSIONS:
        client.send(BEGIN_SEND.encode())
        handle_file(client, file_name, file_extension, int(file_size))
    else:
        client.send(INVALID_EXTENSION.encode())
    thread_mutex.acquire()
    CUR_THREADS -= 1
    print(CUR_THREADS)
    thread_mutex.release()
    client.close()

def handle_file(client, file_name, file_extension, file_size):
    file_bytes = get_client_file(client, file_size)
    new_file_name = handle_file_type(file_bytes, file_name, file_extension)
    # send_file_to_client(client, new_file_name, file_extension)
    # file = open(f"{file_name}{file_extension}", "wb")
    # file.write(file_bytes)
    # file.close()
def get_client_file(client, file_size):
    file_bytes = b""
    fin_msg = f"{FIN}".encode()
    fin_len = len(fin_msg)
    while True:
        data = client.recv(MAX_MSG_SIZE)
        file_bytes += data
        if file_bytes[-fin_len:] == fin_msg:
            file_bytes = file_bytes[:file_size]
            break
    return file_bytes

def handle_file_type(file_bytes, file_name, file_extension):
    new_file_name = f"{file_name}{str(threading.get_ident())}{file_extension}"
    if file_extension in IMG_EXTENSIONS:
        image = np.asarray(bytearray(file_bytes), dtype="uint8")
        image = cv2.imdecode(image, 0)
        # saves image to current directory
        cv2.imwrite(new_file_name, image)
    else:
        pass
    return new_file_name

def send_file_to_client(client, file_name, file_extension):
    pass

def clean_file(file_name):
    pass

if __name__ == '__main__':
    thread_pool = check_input()
    if thread_pool:
        start_server(thread_pool)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
