from lib.stop_and_wait import *

SERVICE_HOST = 'localhost'
SERVICE_PORT = 12000
STORAGE_DIRPATH = './server_storage'


serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((SERVICE_HOST, SERVICE_PORT))

while True:
	print('Listening for clients')
	filename, type, p, clientAddress = recv_data(serverSocket)
	filepath = STORAGE_DIRPATH + '/' + filename
	newServerSocket = socket(AF_INET, SOCK_DGRAM)
	newServerSocket.bind((SERVICE_HOST, SERVICE_PORT+1))
	send_ack(newServerSocket, clientAddress, p)
	if (type == 'DOWN'):
		send_file(newServerSocket, clientAddress, filepath, p+1)
	elif (type == 'FILE'):
		recv_file(newServerSocket, clientAddress, filepath, type)