import threading
import sys
import socket


def check_input():
    if len(sys.argv) != 2:
        print("didn't get thread pool size")
        return
    try:
        thread_pool = int(sys.argv[1])
    except ValueError:
        print("thread pool is not a number, please enter a number between 5-20")
        return
    if thread_pool <= 0:
        print("thread pool must be a number between 5-20")
    return thread_pool

def start_server(thread_pool, listen_port):
    pass


# when server starts, he receives max requests he can process at a time.
# main opens a listening port.
# if a connection is received, server checks if it does not exceed max requests
# if so create a thread that handles that connection.
# The amount of threads currently at work needs to be a global variable that can be accessed (with mutex) by all the
# working threads so that they can update it when they are finished with their task
if __name__ == '__main__':
    thread_pool = check_input()
    start_server(thread_pool, 2000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
