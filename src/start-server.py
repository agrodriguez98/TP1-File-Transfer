from socket import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000

CLIENT_BUFFER_SIZE = 4096
SERVER_BUFFER_SIZE = CLIENT_BUFFER_SIZE + 1 + 4

def recv_data(serverSocket):
	data, clientAddress = serverSocket.recvfrom(SERVER_BUFFER_SIZE)
	p = int.from_bytes(data[:1], 'big')
	print('Received P', p)
	type = data[1:5].decode()
	if (type == 'DONE'):
		payload = type
		return (payload, type, p, clientAddress)
	payload = data[5:]
	if (type == 'DATA'):
		return (payload, type, p, clientAddress)
	else:
		return (payload.decode(), type, p, clientAddress)

def send_ack(serverSocket, clientAddress, p):
	serverSocket.sendto(p.to_bytes(1, 'big') + 'ACK'.encode(), clientAddress)
	print('Sent ACK', p)

def upload(serverSocket, filename, type):
	path = 'server_storage/' + filename
	counter = 0
	with open(path, 'wb') as file:
		while (type != 'DONE'):
			payload, type, p, clientAddress = recv_data(serverSocket)
			send_ack(serverSocket, clientAddress, p)
			if (counter < p and type == 'DATA'):
				file.write(payload)
				counter += 1
	print('Done receiving')

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((SERVER_HOST, SERVER_PORT))

while True:
	print('Ready to receive files')
	filename, type, p, clientAddress = recv_data(serverSocket)
	newServerSocket = socket(AF_INET, SOCK_DGRAM)
	newServerSocket.bind((SERVER_HOST, SERVER_PORT+1))
	send_ack(newServerSocket, clientAddress, p)
	upload(newServerSocket, filename, type)