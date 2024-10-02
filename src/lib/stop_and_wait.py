from socket import *

SENDER_BUFFER_SIZE = 8192

PACKET_NUMBER_BYTES = 2

TYPE_BYTES = 4

RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKET_NUMBER_BYTES + TYPE_BYTES

SENDER_TIMEOUT = 0.09

def verbose_log(message, verbose):
	if verbose:
		print(message)

#
# Sender role
#
def send_data(senderSocket, receiverAddress, data, p, verbose):
	senderSocket.sendto(data, receiverAddress)
	tries = 0
	verbose_log(f'Sent packet {p}', verbose)
	while tries < 10:
		try:
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:PACKET_NUMBER_BYTES], 'big')
			type = receivedData[PACKET_NUMBER_BYTES:PACKET_NUMBER_BYTES+TYPE_BYTES].decode()
			if (type == 'ACKN'):
				verbose_log(f'Received ACK' + ' ' + str(i), verbose)
			p += 1
			return (address, p)
		except timeout:
			tries += 1
			verbose_log(f'Timeout ocurred sending packet {p}', verbose)
			senderSocket.sendto(data, receiverAddress)
			verbose_log(f'Resending packet {p}', verbose)
	verbose_log(f'Connection dropped unexpectedly', verbose)

def send_close(senderSocket, receiverAddress, p, verbose):
	tries = 0
	data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			senderSocket.sendto(data, receiverAddress)
			verbose_log(f'Sending DONE {p}', verbose)
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:PACKET_NUMBER_BYTES], 'big')
			verbose_log(receivedData[PACKET_NUMBER_BYTES:].decode() + ' ' + str(i), verbose)
			verbose_log(f'Ending gracefully', verbose)
			return
		except timeout:
			tries += 1
	verbose_log(f'Ending doubtfully', verbose)

def send_file(senderSocket, receiverAddress, filepath, p, verbose):
	with open(filepath, 'rb') as file:
		bytesRead = file.read(SENDER_BUFFER_SIZE)
		while bytesRead:
			data = p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'DATA'.encode() + bytesRead
			receiverAddress, p = send_data(senderSocket, receiverAddress, data, p, verbose)
			bytesRead = file.read(SENDER_BUFFER_SIZE)
	send_close(senderSocket, receiverAddress, p, verbose)

#
# Receiver role
#
def recv_data(receiverSocket, verbose):
	data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	p = int.from_bytes(data[:PACKET_NUMBER_BYTES], 'big')
	verbose_log(f'Received packet {p}', verbose)
	type = data[PACKET_NUMBER_BYTES:PACKET_NUMBER_BYTES+TYPE_BYTES].decode()
	if (type == 'DONE'):
		payload = type
		return (payload, type, p, senderAddress)
	payload = data[PACKET_NUMBER_BYTES+TYPE_BYTES:]
	if (type == 'DATA'):
		return (payload, type, p, senderAddress)
	else:
		return (payload.decode(), type, p, senderAddress)

def send_ack(receiverSocket, senderAddress, p, verbose):
	receiverSocket.sendto(p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'ACKN'.encode(), senderAddress)
	verbose_log(f'Sent ACK {p}', verbose)

def write_file(filepath, data):
	with open(filepath, 'ab') as file:
		file.write(data)

def recv_file(receiverSocket, senderAddress, filepath, verbose):
	counter = 0
	payload, type, p, senderAddress = recv_data(receiverSocket, verbose)
	send_ack(receiverSocket, senderAddress, p, verbose)
	while (type != 'DONE'):
		if (counter < p and type == 'DATA'):
			write_file(filepath, payload)
			counter += 1
		payload, type, p, senderAddress = recv_data(receiverSocket, verbose)
		send_ack(receiverSocket, senderAddress, p, verbose)
	verbose_log(f'Done receiving', verbose)

def establish_connection(senderSocket, receiverAddress, data, p, verbose):
	senderSocket.sendto(data, receiverAddress)
	tries = 0
	verbose_log(f'Sent initial packet', verbose)
	while tries < 10:
		try:
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:PACKET_NUMBER_BYTES], 'big')
			type = receivedData[PACKET_NUMBER_BYTES:PACKET_NUMBER_BYTES+TYPE_BYTES].decode()
			if (type == 'ACKN'):
				verbose_log(f'Received initial ACK', verbose)
				# p += 1 # aumentar p o no?
				return (address, p)
			if (type == 'ERRO'):
				payload = receivedData[PACKET_NUMBER_BYTES+TYPE_BYTES:]
				print(payload.decode())
				raise Exception("Error when establishing connection")
		except timeout:
			tries += 1
			verbose_log(f'Timeout ocurred sending initial packet', verbose)
			senderSocket.sendto(data, receiverAddress)
			verbose_log(f'Resending initial packet', verbose)
	verbose_log(f'Failed to establish connection', verbose)

def send_error(receiverSocket, senderAddress, p, err_msg, verbose):
	receiverSocket.sendto((p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'ERRO'.encode() + err_msg), senderAddress)
	verbose_log(f'Sent {err_msg.decode()}', verbose)