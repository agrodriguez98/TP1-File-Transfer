"""
Download client
"""

import time
from socket import socket, AF_INET, SOCK_DGRAM
from lib.cli import get_argparser, get_args, App

start_time = time.time()

argsparser = get_argparser(App.CLIENT_DOWNLOAD)
args = get_args(argsparser, App.CLIENT_DOWNLOAD)

if args.modesr:
    from lib.selective_repeat import establish_connection, recv_file
    from lib.selective_repeat import PACKET_NUMBER_BYTES, SENDER_TIMEOUT
else:
    from lib.stop_and_wait import establish_connection, recv_file
    from lib.stop_and_wait import PACKET_NUMBER_BYTES, SENDER_TIMEOUT
    from lib.stop_and_wait import RECEIVER_TIMEOUT

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(SENDER_TIMEOUT)
p = 0
type_msg = 'DOWN'


data = (p.to_bytes(PACKET_NUMBER_BYTES, 'big')
            + type_msg.encode()
            + args.name.encode())
try:
    serverAddress, p = establish_connection(clientSocket, (args.host, args.port), data, p, args.verbose)
except Exception:
    clientSocket.close()
    exit(1)

if args.modesr:
    # Selective repeat
    recv_file(clientSocket, serverAddress, args.dst + '/' + args.name, type, 0, args.verbose)
else:
    # Stop and wait
    clientSocket.settimeout(RECEIVER_TIMEOUT)
    recv_file(clientSocket, serverAddress, args.dst + '/' + args.name, args.verbose)


clientSocket.close()
print(f"--- {time.time() - start_time} seconds ---")
