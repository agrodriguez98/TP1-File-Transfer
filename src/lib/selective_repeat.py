from socket import *
from datetime import datetime

SENDER_BUFFER_SIZE = 4096
PACKAGE_NUMBER_BYTES = 1
TYPE_BYTES = 4
RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKAGE_NUMBER_BYTES + TYPE_BYTES
WINDOW_SIZE = 10
TIMEOUT = 1000000 #microsegundos 

#
# Sender role
#
def send_file(senderSocket, receiverAddress, filepath, seq_number):
	"""
	Declaro window[WINDOW_SIZE]
	Divido archivo en datos_pendientes[]
	Declaro send_base = 0
	Declaro seq_number = 0

	Por cada dato_pendiente:
		if seq_number < send_base + WINDOW_SIZE:
			Envio dato_pendiente
			Pusheo (dato_pendiente, seq_number, timeout) en window
			seq_number++
		else:
			while recibo akc:
				if seq_number_ack == send_base:
					window.pop(0)
					send_base++
			for pendiente in window:
				if pendiente timeout:
					pendiente send
					pendiente timeout update
	while window len > 0:
		while recibo akc:
			if seq_number_ack == send_base:
				window.pop(0)
				send_base++
		for pendiente in window:
			if pendiente timeout:
				pendiente send
				pendiente timeout update
	"""
	senderSocket.setblocking(False)
	window = []
	send_base = seq_number
	file = open(filepath, 'rb')
	bytesRead = file.read(SENDER_BUFFER_SIZE)
	while bytesRead:
		if seq_number < send_base + WINDOW_SIZE:
			data = seq_number.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
			senderSocket.sendto(data, receiverAddress)
			print("enviado paquete"+str(seq_number))
			dt = datetime.now()
			window.append((bytesRead, seq_number, dt.microsecond + TIMEOUT))
			seq_number += 1
		else:
			try:
				receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			except BlockingIOError:
				pass
			while receivedData:
				seq_number_ack = int.from_bytes(receivedData[:1], 'big')
				if seq_number_ack == send_base:
					window.pop(0)
					send_base += 1
				try:
					receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
				except BlockingIOError:
					pass
				
			for pendiente in window:
				dt = datetime.now()
				if dt.microsecond > pendiente[2]:
					data = seq_number.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
					senderSocket.sendto(data, receiverAddress)
					pendiente[2] = dt.microsecond
		bytesRead = file.read(SENDER_BUFFER_SIZE)
	while window.length > 0:
		try:
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
		except BlockingIOError:
			pass
		while receivedData:
			seq_number_ack = int.from_bytes(receivedData[:1], 'big')
			if seq_number_ack == send_base:
				window.pop(0)
				send_base += 1
			try:
				receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			except BlockingIOError:
				pass
			
		for pendiente in window:
			dt = datetime.now()
			if dt.microsecond > pendiente[2]:
				data = seq_number.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
				senderSocket.sendto(data, receiverAddress)
				pendiente[2] = dt.microsecond


#
# Receiver role
#
def recv_file(receiverSocket, senderAddress, filepath, type):

	"""
	Declaro window[] = [None] * WINDOW_SIZE

	Creo archivo
	Declaro rcv_base = 0
	
	Hasta no recibir DONE, y rcv_base == DONE_seq_number:
		leo data
		if seq_number < rcv_base:
			ack seq number
		else if seq_number == rcv_base:
			archivo write data
			ack seq number
			rcv_base ++
			window.pop(0)
			window.append(None)
			while window[0]:
				archivo write window[0]
				window.pop(0)
				window.append(None)
		else if seq_number < rcv_base + WINDOW_SIZE:
			while len(window) < WINDOW_SIZE:
				window.append(None)
			window[seq_number-rcv_base] = data
			ack seq_number
		else:
			do nothing
	"""
	window = [None] * WINDOW_SIZE
	file = open(filepath, 'wb')
	rcv_base = 1
	done_received = False
	done_seq_number = 0
	data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	while data and done_received == False:
		seq_number = int.from_bytes(data[:1], 'big')
		type = data[1:5].decode()
		print("recibido paquete"+str(seq_number))
		if (type == 'DONE'):
			done_received = True
			done_seq_number = seq_number
			send_ack(receiverSocket, senderAddress, seq_number)
		elif(type == 'DATA'):
			payload = data[5:]
			if seq_number < rcv_base:
				send_ack(receiverSocket, senderAddress, seq_number)
			elif seq_number == rcv_base:
				file.write(payload)
				send_ack(receiverSocket, senderAddress, seq_number)
				rcv_base += 1
				window.pop(0)
				window.append(None)
				while window[0]:
					file.write(window[0])
					window.pop(0)
					window.append(None)
			elif seq_number < rcv_base + WINDOW_SIZE:
				while len(window)<WINDOW_SIZE:
					window.append(None)
				window[seq_number-rcv_base] = data
				send_ack(receiverSocket, senderAddress, seq_number)
		data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)


def send_ack(receiverSocket, senderAddress, p):
	receiverSocket.sendto(p.to_bytes(1, 'big') + 'ACK'.encode(), senderAddress)


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