from lib.cli import *
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

data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + type.encode() + args.name.encode()

try:
    serverAddress, p = establish_connection(clientSocket, (args.host, args.port), data, p, args.verbose)
    p+=1
except:
    clientSocket.close()
    exit(1)  

send_file(clientSocket, serverAddress, args.src + '/' +  args.name, p, args.verbose)

clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))

