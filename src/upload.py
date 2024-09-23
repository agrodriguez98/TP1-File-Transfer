from socket import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000

BUFFER_SIZE = 4096

filename = 'AUTH.png'

def send_data(clientSocket, serverAddress, data, p):
	clientSocket.sendto(data, serverAddress)
	print('Sent P', p)
	while True:
		try:
			receivedData, address = clientSocket.recvfrom(BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			p += 1
			return (address, p)
		except timeout:
			print('Timeout ocurred sending packet', p)
			clientSocket.sendto(data, serverAddress)
			print('Resending P', p)

def send_close(clientSocket, serverAddress, p):
	tries = 0
	data = p.to_bytes(1, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			clientSocket.sendto(data, serverAddress)
			print('Sending DONE', p)
			receivedData, address = clientSocket.recvfrom(BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			print('Ending gracefully')
			return
		except timeout:
			tries += 1
	print('Ending doubtfully')

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1);
p = 0
data = p.to_bytes(1, 'big') + 'FILE'.encode() + filename.encode()
serverAddress, p = send_data(clientSocket, (SERVER_HOST, SERVER_PORT), data, p)
with open('files/' + filename, 'rb') as file:
	bytesRead = file.read(BUFFER_SIZE)
	while bytesRead:
		data = p.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
		serverAddress, p = send_data(clientSocket, serverAddress, data, p)
		bytesRead = file.read(BUFFER_SIZE)

send_close(clientSocket, serverAddress, p)
clientSocket.close()