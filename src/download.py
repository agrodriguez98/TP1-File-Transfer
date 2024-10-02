from cli import *
import time

start_time = time.time()

argsparser = get_argparser(App.CLIENT_DOWNLOAD)
args = get_args(argsparser, App.CLIENT_DOWNLOAD)

if args.modesr:
	from lib.selective_repeat import *
else:
	from lib.stop_and_wait import *

clientSocket = socket(AF_INET, SOCK_DGRAM)
p = 0
type = 'DOWN'


# falta cambiar la constanta PACKAGE_NUMBER_BYTES por PACKET_NUMBER_BYTES
if args.modesr:
    # Selective repeat
    data = p.to_bytes(PACKAGE_NUMBER_BYTES, 'big') + type.encode() + args.name.encode()
else:
    # Stop and wait
    data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + type.encode() + args.name.encode()	

serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p, args.verbose)

if args.modesr:
    # Selective repeat
    recv_file(clientSocket, serverAddress, args.dst + '/' + args.name, type, 0, args.verbose)
else:
    # Stop and wait
    recv_file(clientSocket, serverAddress, args.dst + '/' + args.name, args.verbose)


clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))