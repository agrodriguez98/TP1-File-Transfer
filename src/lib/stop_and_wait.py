from socket import *
from time import sleep

SENDER_BUFFER_SIZE = 4096
# Este sería el tamaño del payload? Es fijo, una mejora podría ser hacerlo variable

PACKAGE_NUMBER_BYTES = 1
TYPE_BYTES = 4
FILENAME_BYTES = 8

RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKAGE_NUMBER_BYTES + TYPE_BYTES + FILENAME_BYTES

#
# Sender role
#
def send_data(clientSocket, serverAddress, data, p):
	clientSocket.sendto(data, serverAddress)
	print('Sent P', p)
	while True:
		try:
			sleep(0.2) #Para probarlo con distintos clientes en simultaneo
			receivedData, address = clientSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			p += 1
			return (address, p)
		except timeout:
			print('Timeout ocurred sending packet', p)
			clientSocket.sendto(data, serverAddress)
			print('Resending P', p)

def send_file(clientSocket, serverAddress, SOURCE_FILEPATH, p):
	with open(SOURCE_FILEPATH, 'rb') as file:
		bytesRead = file.read(SENDER_BUFFER_SIZE)
		while bytesRead:
			# hardcodeo filename para rellenar los 8 bytes, capaz no hace falta y se puede sacar
			data = p.to_bytes(1, 'big') + 'DATA'.encode() + 'FILENAME'.encode() + bytesRead
			serverAddress, p = send_data(clientSocket, serverAddress, data, p)
			bytesRead = file.read(SENDER_BUFFER_SIZE)

def send_close(clientSocket, serverAddress, p):
	tries = 0
	data = p.to_bytes(1, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			clientSocket.sendto(data, serverAddress)
			print('Sending DONE', p)
			receivedData, address = clientSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			print('Ending gracefully')
			return
		except timeout:
			tries += 1
	print('Ending doubtfully')
	

	
#
# Receiver role
#

# en este caso creo que no hace falta recibir un ack despues del DOWN
# directamente se puede recibir el archivo
def send_file_request(clientSocket, serverAddress, filename, p):
	
	data = p.to_bytes(1, 'big') + 'DOWN'.encode() + filename.encode()
	clientSocket.sendto(data, serverAddress)
	print('Sent P', p)

def recv_data(clientSocket):
	data, clientAddress = clientSocket.recvfrom(RECEIVER_BUFFER_SIZE)
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
	
def recv_file(receiverSocket, senderAddress, filepath, type):
    # Para que es el counter?
    counter = 0
    with open(filepath, 'wb') as file:
        while (type != 'DONE'):
            sleep(0.2) #Para probarlo con distintos clientes en simultaneo
            payload, type, p = recv_data(receiverSocket)
            send_ack(receiverSocket, senderAddress, p)
            if (counter <= p and type == 'DATA'):
                file.write(payload)
                counter += 1