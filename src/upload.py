from lib.stop_and_wait import *
from cli import *
import time

start_time = time.time()

argsparser = get_argparser(App.CLIENT_UPLOAD)
args = get_args(argsparser, App.CLIENT_UPLOAD)

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(SENDER_TIMEOUT)
p = 0
type = 'FILE'
data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + type.encode() + args.name.encode()
serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p)
send_file(clientSocket, serverAddress, args.src + '/' + args.name, p)
clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))
