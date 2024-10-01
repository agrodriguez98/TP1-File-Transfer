from lib.stop_and_wait import *
from cli import *
import time

start_time = time.time()

argsparser = get_argparser(App.CLIENT_DOWNLOAD)
args = get_args(argsparser, App.CLIENT_DOWNLOAD)

clientSocket = socket(AF_INET, SOCK_DGRAM)

p = 0
type = 'DOWN'
data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + type.encode() + args.name.encode()
serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p)
recv_file(clientSocket, serverAddress, args.dst + '/' + args.name)
clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))
