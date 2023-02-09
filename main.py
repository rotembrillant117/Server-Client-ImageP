import threading
import sys
import socket
import Transformation

LOCAL_HOST = "127.0.0.1"
CUR_THREADS = 0
MAX_QUEUE = 5
PORT = 2001
MAX_MSG_SIZE = 1024
thread_mutex = threading.Lock()
MAX_POOL = 20
MIN_POOL = 5
IMG_EXTENSIONS = {".PNG", ".jpg"}
VID_EXTENSIONS = {".mp4"}
OVERLOADED_MSG = "Server is overloaded, try again later..."
INVALID_EXTENSION = "Didn't receive correct file type"
BEGIN_SEND = "<BEGIN SEND>"
GOT_METADATA = "<GOT METADATA>"
GOT_FILE = "<GOT FILE>"
FIN = "<FIN SEND>"
GS = "Gray-Scale"
PB = "Pyramid Blending"
REQ_FILES = {GS: 1, PB: 2}



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
    # get request type
    request_type = client.recv(MAX_MSG_SIZE).decode()
    print(f"{request_type} {len(request_type)}")
    num_files = REQ_FILES[request_type]
    handle_request(request_type, num_files, client, addr)

    thread_mutex.acquire()
    CUR_THREADS -= 1
    print(CUR_THREADS)
    thread_mutex.release()
    client.close()
def handle_request(request_type, num_files, client, addr):
    file_names = []
    files_bytes = []
    files_extensions = []
    client.send(BEGIN_SEND.encode())
    for i in range(num_files):
        file_info = client.recv(MAX_MSG_SIZE).decode()
        file_name, file_extension, file_size = file_info.split("_")
        print(file_name, file_extension, file_size)
        files_extensions.append(file_extension)
        client.send(f"{GOT_METADATA}".encode())
        file_b = get_client_file(client, int(file_size))
        files_bytes.append(file_b)
        client.send(f"{GOT_FILE}".encode())
        new_file_name = f"{file_name}{file_extension}"
        file_names.append(new_file_name)
    print(file_names)
    print(files_extensions)
    if request_type == GS:
        transformation = Transformation.GrayScale(file_names, files_bytes, files_extensions)
    else:
        transformation = Transformation.GrayScale(file_names, files_bytes, files_extensions)
    transformation.transform()

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


def send_file_to_client(client, file_name, file_extension):
    pass


if __name__ == '__main__':
    thread_pool = check_input()
    if thread_pool:
        start_server(thread_pool)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
