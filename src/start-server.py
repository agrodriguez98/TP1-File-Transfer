from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from lib.selective_repeat import *
from cli import *

N_THREADS = 10

def handle_connection(filename, type, p, clientAddress):
	filepath = args.storage + '/' + filename
	newServerSocket = socket(AF_INET, SOCK_DGRAM)
	newServerSocket.bind((args.host, 0))

	send_ack(newServerSocket, clientAddress, p)
	if (type == 'DOWN'):
		send_file(newServerSocket, clientAddress, filepath, 0)
	elif (type == 'FILE'):
		recv_file(newServerSocket, clientAddress, filepath, type, 1)

argsparser = get_argparser(App.SERVER)
args = get_args(argsparser, App.SERVER)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((args.host, args.port))

with ThreadPoolExecutor(max_workers=N_THREADS) as pool:

	while True:
		print('Listening for clients')
		filename, type, p, clientAddress = recv_data(serverSocket)
		pool.submit(handle_connection, filename, type, p, clientAddress)
		
