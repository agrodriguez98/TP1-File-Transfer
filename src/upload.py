from lib.selective_repeat import *
from cli import *
import time

start_time = time.time()
FILENAME = 'cheems.png' # Quedo del selective repeat

argsparser = get_argparser(App.CLIENT_UPLOAD)
args = get_args(argsparser, App.CLIENT_UPLOAD)

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(SENDER_TIMEOUT)
p = 0
type = 'FILE'

# Stop and wait
# data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + type.encode() + args.name.encode()

# Selective repeat
data = p.to_bytes(1, 'big') + type.encode() + FILENAME.encode()

# Stop and wait
# serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p, args.verbose)

# Selective repeat
serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p)

# Stop and wait
# send_file(clientSocket, serverAddress, args.src + '/' + args.name, p, args.verbose)

# Selective repeat
send_file(clientSocket, serverAddress, args.src + '/' + FILENAME, p)

clientSocket.close()
print("--- %s seconds ---" % (time.time() - start_time))

