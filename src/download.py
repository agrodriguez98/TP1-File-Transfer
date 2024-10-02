from lib.selective_repeat import *
from cli import *
import time

start_time = time.time()
FILENAME = 'cheems.png' # Quedo del selective repeat

argsparser = get_argparser(App.CLIENT_DOWNLOAD)
args = get_args(argsparser, App.CLIENT_DOWNLOAD)

clientSocket = socket(AF_INET, SOCK_DGRAM)
p = 0
type = 'DOWN'

# Stop and wait
# data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + type.encode() + args.name.encode()

# Selective repeat
data = p.to_bytes(1, 'big') + type.encode() + FILENAME.encode()

# Stop and wait
# serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p, args.verbose)

# Selective repeat
serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p)

# Stop and wait
# recv_file(clientSocket, serverAddress, args.dst + '/' + args.name, args.verbose)

# Selective repeat
recv_file(clientSocket, serverAddress, args.dst + '/' + FILENAME, type, 0)

clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))