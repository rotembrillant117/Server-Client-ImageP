import socket
GS = "Gray-Scale"
PB = "Pyramid Blending"
LOCAL_HOST = "127.0.0.1"
PORT = 2001
MAX_MSG_SIZE = 1024
BEGIN_SEND = "<BEGIN SEND>"
FIN = "<FIN SEND>"


def start_client(request_type, files, file_infos):

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("socket creation failed with error: " + str(e))
        return False
    client_socket.connect((LOCAL_HOST, PORT))

    msg = f"{request_type}"
    client_socket.send(msg.encode())
    data = client_socket.recv(MAX_MSG_SIZE).decode()
    if data != BEGIN_SEND:
        print(data)
        return False
    else:
        send_files(files, file_infos, client_socket)
    client_socket.close()
    return True


def send_files(files, file_infos, client_socket):
    for i in range(len(files)):
        cur_info = file_infos[i]
        msg = f"{cur_info[0]}_{cur_info[1]}_{cur_info[2]}"
        client_socket.send(msg.encode())
        print(client_socket.recv(MAX_MSG_SIZE).decode()) # got METADATA
        data = files[i].read()
        files[i].close()
        # print(client_socket.recv(MAX_MSG_SIZE).decode())
        client_socket.sendall(data)
        client_socket.send(f"{FIN}".encode())
        print(client_socket.recv(MAX_MSG_SIZE).decode()) # got FILE
def get_files(file_paths):
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

    start_client(request_type, files, file_infos)

if __name__ == '__main__':
    # if len(sys.argv) == 2:
    #     start_client(sys.argv[1])
    pass
