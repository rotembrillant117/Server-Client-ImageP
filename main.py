import threading
import sys
import socket
import Transformation
import os
import shutil
from constants import *

LOCAL_HOST = "127.0.0.1"
CUR_THREADS = 0
MAX_QUEUE = 5
thread_mutex = threading.Lock()
MAX_POOL = 20
MIN_POOL = 5
OVERLOADED_MSG = "Server is overloaded, try again later..."
INVALID_EXTENSION = "Didn't receive correct file type"
GOT_METADATA = "<GOT METADATA>"
REQ_FILES = {GS: 1, PB: 2}
REQ_TYPES = {GS, PB}
TYPE_TO_TRANS = {GS: Transformation.GrayScale, PB: Transformation.PyramidBlend}



def check_input():
    """
    Checks the size of the thread pool that was given
    :return: Size of thread pool if size is between 5-20, else False
    """
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
    """
    Starts the server with a specific thread pool and establishes connections between clients. Each client is handled
    by his own thread
    :param thread_pool: The max amount of threads allowed
    :return:
    """
    try:
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("socket creation failed with error: " + str(e))
        return
    listen_socket.bind((LOCAL_HOST, PORT))
    listen_socket.listen(MAX_QUEUE)
    global CUR_THREADS
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
    """
    This function handles a client request. Also makes a working directory for the current thread in which files will be
    saved. When client request process is complete, the result will be sent to the client and later the thread working
    directory will be deleted. Finally, the current working threads will be updated, and server-client connection
    terminated
    :param client: client socket connection
    :param addr: client address
    :return:
    """
    print(f"got connection from: {addr}")
    global CUR_THREADS
    request_type = client.recv(MAX_MSG_SIZE).decode()
    if request_type not in REQ_TYPES:
        return
    num_files = REQ_FILES[request_type]
    cwd = os.getcwd()
    thread_dir = os.path.join(cwd, str(threading.get_ident()))
    os.mkdir(thread_dir)
    handle_request(request_type, num_files, client, thread_dir)
    shutil.rmtree(thread_dir)

    thread_mutex.acquire()
    CUR_THREADS -= 1
    print(CUR_THREADS)
    thread_mutex.release()
    client.close()
def handle_request(request_type, num_files, client, thread_dir):
    """
    This function processes the client request-type
    :param request_type: the client request type
    :param num_files: the expected files to receive
    :param client: client socket
    :param thread_dir: thread working dir
    :return:
    """
    new_file_names = []
    files_bytes = []
    files_extensions = []
    client.send(BEGIN_SEND.encode())
    for i in range(num_files):
        file_info = client.recv(MAX_MSG_SIZE).decode()
        file_name, file_extension, file_size = file_info.split("_")
        files_extensions.append(file_extension)
        client.send(f"{GOT_METADATA}".encode())
        files_bytes.append(get_client_file(client, int(file_size)))
        client.send(f"{GOT_FILE}".encode())
        new_file_names.append(f"{file_name}{file_extension}")
    transformation = TYPE_TO_TRANS[request_type](new_file_names, files_bytes, files_extensions, thread_dir)
    f_to_send, f_to_send_extension = transformation.transform()
    send_file_to_client(client, f_to_send, os.path.join(thread_dir, f_to_send), f_to_send_extension)

def get_client_file(client, file_size):
    """
    This function gets a file sent from the client
    :param client: client socket
    :param file_size: the expected file size
    :return: file bytes
    """
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


def send_file_to_client(client, file_name, file_location, file_extension):
    """
    This function sends the output file (after completing the client request) to the client
    :param client: client socket
    :param file_name: name of output file
    :param file_location: location of output file
    :param file_extension: extension of output file (currently not in use, maybe of use in the future)
    :return:
    """
    file_size = os.path.getsize(file_location)
    client.send(f"{REQUEST_PROCESSED}".encode())
    client.recv(MAX_MSG_SIZE).decode()
    client.send(f"Client{file_name}_{file_size}".encode())
    f = open(file_location, 'rb')
    data = f.read()
    f.close()
    client.sendall(data)
    client.send(f"{FIN}".encode())
    client.recv(MAX_MSG_SIZE).decode() # GOT FILE


if __name__ == '__main__':
    thread_pool = check_input()
    if thread_pool:
        start_server(thread_pool)

