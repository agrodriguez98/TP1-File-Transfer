from socket import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000

CLIENT_BUFFER_SIZE = 4096
SERVER_BUFFER_SIZE = CLIENT_BUFFER_SIZE + 1 + 4

def send_data(serverSocket, clientAddress, data, p):
	serverSocket.sendto(data, clientAddress)
	print('Sent P', p)
	while True:
		try:
			receivedData, address = serverSocket.recvfrom(CLIENT_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			p += 1
			return (address, p)
		except timeout:
			print('Timeout ocurred sending packet', p)
			serverSocket.sendto(data, clientAddress)
			print('Resending P', p)

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

def send_close(serverSocket, clientAddress, p):
	tries = 0
	data = p.to_bytes(1, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			serverSocket.sendto(data, clientAddress)
			print('Sending DONE', p)
			receivedData, address = serverSocket.recvfrom(CLIENT_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			print('Ending gracefully')
			return
		except timeout:
			tries += 1
	print('Ending doubtfully')

def upload(serverSocket, clientAddress, filename, type):
	path = '/home/smarczewski/Documents/TP1-File-Transfer/src/server_storage/' + filename
	counter = 0
	with open(path, 'wb') as file:
		while (type != 'DONE'):
			payload, type, p, clientAddress = recv_data(serverSocket)
			send_ack(serverSocket, clientAddress, p)
			if (counter < p and type == 'DATA'):
				file.write(payload)
				counter += 1
	print('Done receiving')

def download(serverSocket, clientAddress, filename, type):
	path = '/home/smarczewski/Documents/TP1-File-Transfer/src/server_storage/' + filename
	p = 0
	with open(path, 'rb') as file:
		bytesRead = file.read(CLIENT_BUFFER_SIZE)
		while bytesRead:
			data = p.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
			clientAddress, p = send_data(serverSocket, clientAddress, data, p)
			bytesRead = file.read(CLIENT_BUFFER_SIZE)
	send_close(serverSocket, clientAddress, p)



serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((SERVER_HOST, SERVER_PORT))

while True:
	print('Listening for clients')
	filename, type, p, clientAddress = recv_data(serverSocket)
	newServerSocket = socket(AF_INET, SOCK_DGRAM)
	newServerSocket.bind((SERVER_HOST, SERVER_PORT+1))

	if (type == 'DOWN'):
		send_ack(newServerSocket, clientAddress, p)
		download(newServerSocket, clientAddress, filename, type)
	else:
		send_ack(newServerSocket, clientAddress, p)
		upload(newServerSocket, clientAddress, filename, type)