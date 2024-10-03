"""
Upload client
"""
import time
from socket import socket, AF_INET, SOCK_DGRAM
from lib.cli import get_argparser, get_args, App

start_time = time.time()

argsparser = get_argparser(App.CLIENT_UPLOAD)
args = get_args(argsparser, App.CLIENT_UPLOAD)

if args.modesr:
    print("MODESR ON")
    from lib.selective_repeat import establish_connection, send_file
    from lib.selective_repeat import PACKET_NUMBER_BYTES, SENDER_TIMEOUT
else:
    from lib.stop_and_wait import establish_connection, send_file
    from lib.stop_and_wait import PACKET_NUMBER_BYTES, SENDER_TIMEOUT

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(SENDER_TIMEOUT)
p = 0
type_msg = 'FILE'

data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + type_msg.encode() + args.name.encode()

try:
    serverAddress, p = establish_connection(clientSocket, (args.host, args.port), data, p, args.verbose)
    p += 1
except Exception:
    print("FALLÓ")
    clientSocket.close()
    exit(1)

send_file(clientSocket, serverAddress, args.src + '/' + args.name, p, args.verbose)

clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))
