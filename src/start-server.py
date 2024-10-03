"""
Server
"""
from socket import socket, AF_INET, SOCK_DGRAM
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from lib.cli import get_argparser, get_args, App

N_THREADS = 10


def handle_connection(filename, type, p, clientAddress):
    filepath = args.storage + '/' + filename
    newServerSocket = socket(AF_INET, SOCK_DGRAM)
    newServerSocket.bind((args.host, 0))
    print("Handling connection")
    send_ack(newServerSocket, clientAddress, p, args.verbose)
    if (type == 'DOWN'):
        newServerSocket.settimeout(SENDER_TIMEOUT)

        # Este if está porque sr recibe 0 y sw p+1
        if args.modesr:
            # Selective repeat
            send_file(newServerSocket, clientAddress, filepath, 0, args.verbose)
        else:
            # Stop and wait
            send_file(newServerSocket, clientAddress, filepath, p+1, args.verbose)

    elif type == 'FILE':
        if args.modesr:
            # Selective repeat
            recv_file(newServerSocket, clientAddress, filepath, type, 1, args.verbose)
        else:
            # Stop and wait
            newServerSocket.settimeout(RECEIVER_TIMEOUT)
            recv_file(newServerSocket, clientAddress, filepath, args.verbose)

    newServerSocket.close()


argsparser = get_argparser(App.SERVER)
args = get_args(argsparser, App.SERVER)

if args.modesr:
    from lib.selective_repeat import recv_data, send_file, recv_file, send_error
    from lib.selective_repeat import send_ack, SENDER_TIMEOUT
else:
    from lib.stop_and_wait import recv_data, send_file, send_error
    from lib.stop_and_wait import recv_file, send_ack
    from lib.stop_and_wait import RECEIVER_TIMEOUT, SENDER_TIMEOUT

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((args.host, args.port))

with ThreadPoolExecutor(max_workers=N_THREADS) as pool:

    while True:
        print('Listening for clients')

        filename, type, p, clientAddress = recv_data(serverSocket, args.verbose)

        if (type == 'DOWN'):
            if not Path(args.storage + '/' + filename).exists():
                err_msg = f"ERROR: The server storage doesn't contain the file {filename}".encode()
                continue
        elif (type == 'FILE'):
            if Path(args.storage + '/' + filename).exists():
                err_msg = f"ERROR: The server storage already contains a file named {filename}".encode()
                send_error(serverSocket, clientAddress, p, err_msg, args.verbose)
                continue

        pool.submit(handle_connection, filename, type, p, clientAddress)
