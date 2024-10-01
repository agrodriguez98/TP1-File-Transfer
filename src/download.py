from lib.selective_repeat import *
from cli import *

FILENAME = 'cheems.png'

argsparser = get_argparser(App.CLIENT_DOWNLOAD)
args = get_args(argsparser, App.CLIENT_DOWNLOAD)
	
clientSocket = socket(AF_INET, SOCK_DGRAM)
#clientSocket.settimeout(2)
p = 0
type = 'DOWN'
data = p.to_bytes(1, 'big') + type.encode() + FILENAME.encode()
serverAddress, p = send_data(clientSocket, (args.host, args.port), data, p)
recv_file(clientSocket, serverAddress, args.dst + '/' + FILENAME, type, 0)
clientSocket.close()