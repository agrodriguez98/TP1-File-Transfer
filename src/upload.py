from lib.selective_repeat import *
from cli import *

FILENAME = 'cheems.png'

argsparser = get_argparser(App.CLIENT_UPLOAD)
args = get_args(argsparser, App.CLIENT_UPLOAD)

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
p = 0
type = 'FILE'
data = p.to_bytes(1, 'big') + type.encode() + FILENAME.encode()
serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p)
send_file(clientSocket, serverAddress, args.src + '/' + FILENAME, p)
clientSocket.close()