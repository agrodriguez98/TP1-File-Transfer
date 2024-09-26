from socket import *
from sys import argv
from time import sleep

SERVER_HOST = 'localhost'
SERVER_PORT = 12000

BUFFER_SIZE = 4096
SERVER_BUFFER_SIZE = BUFFER_SIZE + 1 + 4 + 8

filename = argv[1]
# El tamaño del filename esta hardcodeado en 8 bytes
# después hay que mejorarlo

# en este caso creo que no hace falta recibir un ack despues del DOWN
# directamente se puede recibir el archivo
def send_data(clientSocket, serverAddress, data, p):
	clientSocket.sendto(data, serverAddress)
	print('Sent P', p)
	

"""
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
"""
def recv_data(clientSocket):
	data, clientAddress = clientSocket.recvfrom(SERVER_BUFFER_SIZE)
	p = int.from_bytes(data[:1], 'big')
	print('Received P', p)
	type = data[1:5].decode()
	filename = data[5:13].decode()
	# aca no hace falta usar el filename
	payload = None
	if (type == 'DATA'):
		payload = data[13:]
	return payload, type, p

def send_ack(clientSocket, serverAddress, p):
	clientSocket.sendto(p.to_bytes(1, 'big') + 'ACK1'.encode(), serverAddress)
	print('Sent ACK', p)
	
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
serverAddress = (SERVER_HOST, SERVER_PORT)
counter = 0
data = counter.to_bytes(1, 'big') + 'DOWN'.encode() + filename.encode()
send_data(clientSocket, serverAddress, data, counter)
with open('files/' + filename, 'wb') as file:
    while (type != 'DONE'):
        sleep(0.2) #Para probarlo con distintos clientes en simultaneo
        payload, type, p = recv_data(clientSocket)
        send_ack(clientSocket, serverAddress, p)
        if (counter <= p and type == 'DATA'):
            file.write(payload)
            #counter += 1
print('Done receiving')