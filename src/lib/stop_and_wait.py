from socket import *
from time import sleep

SENDER_BUFFER_SIZE = 4096
# Este sería el tamaño del payload? Es fijo, una mejora podría ser hacerlo variable

PACKAGE_NUMBER_BYTES = 1
TYPE_BYTES = 4
FILENAME_BYTES = 8

RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKAGE_NUMBER_BYTES + TYPE_BYTES + FILENAME_BYTES


def verbose_log(message, verbose):
	if verbose:
		print(message)

#
# Sender role
#
def send_upload_request(clientSocket, serverAddress, filename, p, verbose):
	filename_len = len(filename).to_bytes(1, 'big')
	data = p.to_bytes(1, 'big') + 'FILE'.encode() + filename_len + filename.encode()
	return send_data(clientSocket, serverAddress, data, p, verbose)

def send_data(clientSocket, serverAddress, data, p, verbose):
	clientSocket.sendto(data, serverAddress)
	verbose_log(f'Sent P {p}', verbose)
	while True:
		try:
			sleep(0.2) #Para probarlo con distintos clientes en simultaneo
			receivedData, address = clientSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			verbose_log(receivedData[1:].decode() + ' ' + str(i), verbose)
			p += 1
			return p
		except timeout:
			verbose_log(f'Timeout ocurred sending packet {p}', verbose)
			clientSocket.sendto(data, serverAddress)
			verbose_log(f'Resending P {p}', verbose)

def send_file(clientSocket, serverAddress, SOURCE_FILEPATH, p, verbose):
	with open(SOURCE_FILEPATH, 'rb') as file:
		bytesRead = file.read(SENDER_BUFFER_SIZE)
		while bytesRead:
			data = p.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
			p = send_data(clientSocket, serverAddress, data, p, verbose)
			bytesRead = file.read(SENDER_BUFFER_SIZE)

def send_close(clientSocket, serverAddress, p, verbose):
	tries = 0
	data = p.to_bytes(1, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			clientSocket.sendto(data, serverAddress)
			verbose_log(f'Sending DONE {p}', verbose)
			receivedData, address = clientSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			verbose_log(receivedData[1:].decode() + ' ' + str(i), verbose)
			verbose_log('Ending gracefully', verbose)
			return
		except timeout:
			tries += 1
	verbose_log('Ending doubtfully', verbose)
	
#
# Receiver role
#

# en este caso creo que no hace falta recibir un ack despues del DOWN
# directamente se puede recibir el archivo
def send_download_request(clientSocket, serverAddress, filename, p, verbose):
	filename_len = len(filename).to_bytes(1, 'big')
	data = p.to_bytes(1, 'big') + 'DOWN'.encode() + filename_len + filename.encode()
	clientSocket.sendto(data, serverAddress)
	verbose_log(f'Sent P {p}', verbose)

def recv_data(clientSocket, verbose):
	data, clientAddress = clientSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	p = int.from_bytes(data[:1], 'big')
	verbose_log(f'Received P {p}', verbose)
	type = data[1:5].decode()
	payload = None
	if (type == 'DATA'):
		payload = data[5:]
	return payload, type, p

def send_ack(clientSocket, serverAddress, p, verbose):
	clientSocket.sendto(p.to_bytes(1, 'big') + 'ACK1'.encode(), serverAddress)
	verbose_log(f'Sent ACK {p}', verbose)
	
def recv_file(receiverSocket, senderAddress, filepath, type, verbose):
    # Para que es el counter?
    counter = 0
    with open(filepath, 'wb') as file:
        while (type != 'DONE'):
            sleep(0.2) #Para probarlo con distintos clientes en simultaneo
            payload, type, p = recv_data(receiverSocket, verbose)
            send_ack(receiverSocket, senderAddress, p, verbose)
            if (counter <= p and type == 'DATA'):
                file.write(payload)
                counter += 1