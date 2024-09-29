from socket import *

SENDER_BUFFER_SIZE = 8192

PACKET_NUMBER_BYTES = 2

TYPE_BYTES = 4

RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKET_NUMBER_BYTES + TYPE_BYTES

#
# Sender role
#
def send_data(senderSocket, receiverAddress, data, p):
	senderSocket.sendto(data, receiverAddress)
	print('Sent packet', p)
	while True:
		try:
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:PACKET_NUMBER_BYTES], 'big')
			type = receivedData[PACKET_NUMBER_BYTES:PACKET_NUMBER_BYTES+TYPE_BYTES].decode()
			if (type == 'ACKN'):
				print('Received ACK' + ' ' + str(i))
			p += 1
			return (address, p)
		except timeout:
			print('Timeout ocurred sending packet', p)
			senderSocket.sendto(data, receiverAddress)
			print('Resending packet', p)

def send_close(senderSocket, receiverAddress, p):
	tries = 0
	data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			senderSocket.sendto(data, receiverAddress)
			print('Sending DONE', p)
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:PACKET_NUMBER_BYTES], 'big')
			print(receivedData[PACKET_NUMBER_BYTES:].decode() + ' ' + str(i))
			print('Ending gracefully')
			return
		except timeout:
			tries += 1
	print('Ending doubtfully')

def send_file(senderSocket, receiverAddress, filepath, p):
	with open(filepath, 'rb') as file:
		bytesRead = file.read(SENDER_BUFFER_SIZE)
		while bytesRead:
			data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'DATA'.encode() + bytesRead
			receiverAddress, p = send_data(senderSocket, receiverAddress, data, p)
			bytesRead = file.read(SENDER_BUFFER_SIZE)
	send_close(senderSocket, receiverAddress, p)

#
# Receiver role
#
def recv_data(receiverSocket):
	data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	p = int.from_bytes(data[:PACKET_NUMBER_BYTES], 'big')
	print('Received packet', p)
	type = data[PACKET_NUMBER_BYTES:PACKET_NUMBER_BYTES+TYPE_BYTES].decode()
	if (type == 'DONE'):
		payload = type
		return (payload, type, p, senderAddress)
	payload = data[PACKET_NUMBER_BYTES+TYPE_BYTES:]
	if (type == 'DATA'):
		return (payload, type, p, senderAddress)
	else:
		return (payload.decode(), type, p, senderAddress)

def send_ack(receiverSocket, senderAddress, p):
	receiverSocket.sendto(p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'ACKN'.encode(), senderAddress)
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
