from socket import *

SENDER_BUFFER_SIZE = 4096

PACKAGE_NUMBER_BYTES = 1

TYPE_BYTES = 4

RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKAGE_NUMBER_BYTES + TYPE_BYTES

#
# Sender role
#
def send_data(senderSocket, receiverAddress, data, p):
	senderSocket.sendto(data, receiverAddress)
	print('Sent P', p)
	while True:
		try:
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			p += 1
			return (address, p)
		except timeout:
			print('Timeout ocurred sending packet', p)
			senderSocket.sendto(data, receiverAddress)
			print('Resending P', p)

def send_close(senderSocket, receiverAddress, p):
	tries = 0
	data = p.to_bytes(1, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			senderSocket.sendto(data, receiverAddress)
			print('Sending DONE', p)
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			print('Ending gracefully')
			return
		except timeout:
			tries += 1
	print('Ending doubtfully')

def send_file(senderSocket, receiverAddress, filepath, p):
	with open(filepath, 'rb') as file:
		bytesRead = file.read(SENDER_BUFFER_SIZE)
		while bytesRead:
			data = p.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
			receiverAddress, p = send_data(senderSocket, receiverAddress, data, p)
			bytesRead = file.read(SENDER_BUFFER_SIZE)
	send_close(senderSocket, receiverAddress, p)

#
# Receiver role
#
def recv_data(receiverSocket):
	data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	p = int.from_bytes(data[:1], 'big')
	print('Received P', p)
	type = data[1:5].decode()
	if (type == 'DONE'):
		payload = type
		return (payload, type, p, senderAddress)
	payload = data[5:]
	if (type == 'DATA'):
		return (payload, type, p, senderAddress)
	else:
		return (payload.decode(), type, p, senderAddress)

def send_ack(receiverSocket, senderAddress, p):
	receiverSocket.sendto(p.to_bytes(1, 'big') + 'ACK'.encode(), senderAddress)
	print('Sent ACK', p)

def recv_file(receiverSocket, senderAddress, filepath, type):
	counter = 0
	with open(filepath, 'wb') as file:
		while (type != 'DONE'):
			payload, type, p, senderAddress = recv_data(receiverSocket)
			send_ack(receiverSocket, senderAddress, p)
			if (counter < p and type == 'DATA'):
				file.write(payload)
				counter += 1
	print('Done receiving')