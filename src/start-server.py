from pathlib import Path
from lib.stop_and_wait import *
from cli import *

argsparser = get_argparser(App.SERVER)
args = get_args(argsparser, App.SERVER)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((args.host, args.port))

print(args)

while True:
	print('Listening for clients')
	filename, type, p, clientAddress = recv_data(serverSocket)
	filepath = args.storage + '/' + filename
	newServerSocket = socket(AF_INET, SOCK_DGRAM)
	newServerSocket.bind((args.host, args.port+1))
	send_ack(newServerSocket, clientAddress, p)
	if (type == 'DOWN'):
		send_file(newServerSocket, clientAddress, filepath, p+1)
	elif (type == 'FILE'):
		recv_file(newServerSocket, clientAddress, filepath, type)


