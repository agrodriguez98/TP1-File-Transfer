from socket import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000

BUFFER_SIZE = 4096
SERVER_BUFFER_SIZE = BUFFER_SIZE + 1 + 4

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

def recv_data(clientSocket):
	data, clientAddress = clientSocket.recvfrom(SERVER_BUFFER_SIZE)
	p = int.from_bytes(data[:1], 'big')
	print('Received P', p)
	type = data[1:5].decode()
	if (type == 'DONE'):
		payload = type
		return (payload, type, p, serverAddress)
	payload = data[5:]
	if (type == 'DATA'):
		return (payload, type, p, serverAddress)
	else:
		return (payload.decode(), type, p, serverAddress)

def send_ack(clientSocket, serverAddress, p):
	clientSocket.sendto(p.to_bytes(1, 'big') + 'ACK'.encode(), serverAddress)
	print('Sent ACK', p)
	
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
counter = 0
data = counter.to_bytes(1, 'big') + 'DOWN'.encode() + filename.encode()
serverAddress, p = send_data(clientSocket, (SERVER_HOST, SERVER_PORT), data, counter)
with open('files/' + filename, 'wb') as file:
    while (type != 'DONE'):
        payload, type, p, serverAddress = recv_data(clientSocket)
        send_ack(clientSocket, serverAddress, p)
        if (counter <= p and type == 'DATA'):
            file.write(payload)
            counter += 1
print('Done receiving')