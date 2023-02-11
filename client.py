import socket
from constants import *
import sys
import os
import random


def start_client(request_type, files, file_infos):
    """
    This function inits a connection with the server, and in the end the output file of the desired request will be
     saved
    :param request_type: The desired request
    :param files: The required files
    :param file_infos: files information
    :return:
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("socket creation failed with error: " + str(e))
        return False
    client_socket.connect((LOCAL_HOST, PORT))

    client_socket.send(request_type.encode())
    data = client_socket.recv(MAX_MSG_SIZE).decode()
    if data != BEGIN_SEND:
        return False
    else:
        send_files(files, file_infos, client_socket)
        receive_server_file(client_socket)
    client_socket.close()
    return True


def send_files(files, file_infos, client_socket):
    """
    This function sends to the server the required amount of files for the specified request type
    :param files: the files to send to server
    :param file_infos: files information
    :param client_socket: client socket
    :return:
    """
    for i in range(len(files)):
        cur_info = file_infos[i]
        send_meta_data(client_socket, cur_info)
        data = files[i].read()
        files[i].close()
        client_socket.sendall(data)
        client_socket.send(FIN.encode())
        print(client_socket.recv(MAX_MSG_SIZE).decode()) # got FILE


def send_meta_data(client_socket, files_info):
    """
    This function sends the meta-data of the files
    :param client_socket: the client socket
    :param files_info: the meta-data to send
    :return:
    """
    for i in range(len(files_info)):
        client_socket.send(f"{files_info[i]}".encode())
        client_socket.recv(MAX_MSG_SIZE).decode()


def get_meta_data(client_socket):
    """
    This function gets the meta-data from the output file that was created by the server
    :param client_socket: the client socket
    :return: file_name, file_size
    """
    file_extension = client_socket.recv(MAX_MSG_SIZE).decode()
    client_socket.send(GOT_METADATA.encode())
    file_size = int(client_socket.recv(MAX_MSG_SIZE).decode())
    client_socket.send(GOT_METADATA.encode())
    return file_extension, file_size


def receive_server_file(client_socket):
    """
    This function receives the output file from the server and saves
    :param client_socket: client socket
    :return:
    """
    print(client_socket.recv(MAX_MSG_SIZE).decode())
    client_socket.send(BEGIN_SEND.encode())
    file_extension, file_size = get_meta_data(client_socket)
    file_bytes = b""
    fin_msg = FIN.encode()
    fin_len = len(fin_msg)
    while True:
        data = client_socket.recv(MAX_MSG_SIZE)
        file_bytes += data
        if file_bytes[-fin_len:] == fin_msg:
            file_bytes = file_bytes[:int(file_size)]
            break
    client_socket.send(GOT_FILE.encode())
    file = open(f"{random.randint(1,10000)}{file_extension}", "wb")
    file.write(file_bytes)
    file.close()


def get_files(file_paths):
    """
    This function creates the file objects from the specified file_paths
    :param file_paths: paths of files
    :return: list of file objects
    """
    files = []
    for i in range(len(file_paths)):
        try:
            f = open(file_paths[i], 'rb')
            files.append(f)
        except OSError:
            print(f"Couldn't open file: {file_paths[i]}")
            return []
    return files


def handle_request(request_type, file_info):
    """
    This function handles a client request
    :param request_type: the request type
    :param file_info: the file info, for example: [[file_path_1, file_extension_1, file_size_1],
    [file_path_2, file_extension_2, file_size_2]]
    :return:
    """
    file_paths = []
    file_infos = []
    for i in range(len(file_info)):
        file_paths.append(file_info[i][0])
        file_infos.append(file_info[i][1:])
    files = get_files(file_paths)
    if len(files) == 0:
        print("Couldn't open files")
        return False
    return start_client(request_type, files, file_infos)

if __name__ == '__main__':
    # file_path = sys.argv[1]
    # file_size = os.path.getsize(file_path)
    # file_name = "VID-20230118-WA0000"
    # file_extension = ".mp4"
    # request = [GS, [file_path, file_name, file_extension, file_size]]
    # handle_request(request)
    pass
