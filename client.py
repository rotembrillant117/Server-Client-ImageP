import socket
from constants import *


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

    client_socket.send(f"{request_type}".encode())
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
        msg = f"{cur_info[0]}_{cur_info[1]}_{cur_info[2]}"
        client_socket.send(msg.encode())
        print(client_socket.recv(MAX_MSG_SIZE).decode()) # got METADATA
        data = files[i].read()
        files[i].close()
        client_socket.sendall(data)
        client_socket.send(f"{FIN}".encode())
        print(client_socket.recv(MAX_MSG_SIZE).decode()) # got FILE

def receive_server_file(client_socket):
    """
    This function receives the output file from the server and saves
    :param client_socket: client socket
    :return:
    """
    print(client_socket.recv(MAX_MSG_SIZE).decode())
    client_socket.send(f"{BEGIN_SEND}".encode())
    file_name, file_size = client_socket.recv(MAX_MSG_SIZE).decode().split("_")
    file_bytes = b""
    fin_msg = f"{FIN}".encode()
    fin_len = len(fin_msg)
    while True:
        data = client_socket.recv(MAX_MSG_SIZE)
        file_bytes += data
        if file_bytes[-fin_len:] == fin_msg:
            file_bytes = file_bytes[:int(file_size)]
            break
    client_socket.send(f"{GOT_FILE}".encode())
    file = open(file_name, "wb")
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

def handle_request(request_info):
    """
    This function handles a request from a client to the server
    :param request_info: example of request [PB, [file_path_1, file_name_1, file_extension_1, file_size_1],
    [file_path_2, file_name_2, file_extension_2, file_size_2]
    :return:
    """
    request_type = request_info[0]
    file_paths = []
    file_infos = []
    for i in range(1, len(request_info)):
        file_paths.append(request_info[i][0])
        file_infos.append(request_info[i][1:])
    files = get_files(file_paths)
    if len(files) == 0:
        print("Couldn't open files")
        return False
    return start_client(request_type, files, file_infos)

if __name__ == '__main__':
    pass
