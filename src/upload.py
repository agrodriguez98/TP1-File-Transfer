from cli import *
import time

start_time = time.time()

argsparser = get_argparser(App.CLIENT_UPLOAD)
args = get_args(argsparser, App.CLIENT_UPLOAD)

if args.modesr:
    from lib.selective_repeat import *
else:
    from lib.stop_and_wait import *

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(SENDER_TIMEOUT)
p = 0
type = 'FILE'

# falta cambiar la constanta PACKAGE_NUMBER_BYTES por PACKET_NUMBER_BYTES
if args.modesr:
    data = p.to_bytes(1, 'big') + type.encode() + args.name.encode()
else:
    data = p.to_bytes(2, 'big') + type.encode() + args.name.encode()

serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p, args.verbose)

send_file(clientSocket, serverAddress, args.src + '/' +  args.name, p, args.verbose)

clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))

