from socket import *
from datetime import datetime
import time
import random
random.seed() 

SENDER_BUFFER_SIZE = 8000
PACKAGE_NUMBER_BYTES = 1 # Quedo del selective repeat
PACKET_NUMBER_BYTES = 2 # El que usamos ahora en Stop and wait
TYPE_BYTES = 4
RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKAGE_NUMBER_BYTES + TYPE_BYTES
WINDOW_SIZE = 10

TIMEOUT = 1
PACKET_LOSS_PERCENTAGE = 0

SENDER_TIMEOUT = 0.09

#
# Sender role
#
def send_file(senderSocket, receiverAddress, filepath, seq_number, verbose):
	bool_window= [False]*WINDOW_SIZE

	senderSocket.setblocking(False)
	window = []
	send_base = seq_number
	file = open(filepath, 'rb')
	bytesRead = file.read(SENDER_BUFFER_SIZE)
	endparse = False
	while bytesRead or len(window) > 0:

		verbose_log(send_base, verbose)
		array_numeros = [int(b) for b in bool_window]
		verbose_log(array_numeros, verbose)
		if seq_number < send_base + WINDOW_SIZE and bytesRead:
			data = seq_number.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
		
			if random.random() > PACKET_LOSS_PERCENTAGE:
				senderSocket.sendto(data, receiverAddress)
			window.append((data, seq_number, time.time() + TIMEOUT))
			seq_number += 1
			bytesRead = file.read(SENDER_BUFFER_SIZE)
		else:			
			"""
			recibidor de acks:
			"""
			try:
				receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			except BlockingIOError:
				receivedData = None
			while receivedData:
				seq_number_ack = int.from_bytes(receivedData[:1], 'big')
				i = 0
				while i < len(window):
					if window[i][1] == seq_number_ack:
						window.pop(i)
						bool_window[seq_number_ack-send_base] = True
						while bool_window[0]==True: 
							bool_window.pop(0)
							send_base+=1
							bool_window.append(False)
					else:
						i += 1
				try:
					receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
				except BlockingIOError:
					receivedData = None
			"""
			reenviar paquetes timeout:
			"""
			for i in range(len(window)):
				if time.time() > window[i][2]:
					data = window[i][0]
					if random.random() > PACKET_LOSS_PERCENTAGE:
						senderSocket.sendto(data, receiverAddress)
					window[i] = (window[i][0], window[i][1], time.time() + TIMEOUT)
		"""
		Si no hay más archivo para leer, aún no se envó el done y no quedan elementos en la ventana de envios, enviar DONE:
		"""
		if not(bytesRead) and not(endparse) and len(window)==0:
			endparse = True
			verbose_log("FIN PARSEO ARCHIVO", verbose)
			type = 'DONE'
			data = seq_number.to_bytes(1, 'big') + type.encode()
			if random.random() > PACKET_LOSS_PERCENTAGE:
				senderSocket.sendto(data, receiverAddress)
			seq_number+=1
			#window.append((data, seq_number, time.time() + TIMEOUT))

#
# Receiver role
#
def recv_file(receiverSocket, senderAddress, filepath, type, seq_number, verbose):
	window= [None]*WINDOW_SIZE
	file = open(filepath, 'wb')
	rcv_base = seq_number
	done_received = False
	done_seq_number = 0

	data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	while True:
		seq_number = int.from_bytes(data[:1], 'big')
		type = data[1:5].decode()
		if (type == 'DONE'):
			
			verbose_log("DONE", verbose)
			done_seq_number = seq_number
			done_received = True
			verbose_log(f'{rcv_base} {done_seq_number}', verbose)
			
			send_ack(receiverSocket, senderAddress, seq_number, verbose)
		elif(type == 'DATA'):
			payload = data[5:]
			if seq_number < rcv_base:
				send_ack(receiverSocket, senderAddress, seq_number, verbose)
				verbose_log("repeated", verbose)

			elif seq_number < rcv_base + WINDOW_SIZE:
				send_ack(receiverSocket, senderAddress, seq_number, verbose)
				window[seq_number-rcv_base]=payload

			else:
				verbose_log("out of window", verbose)
		else:
			verbose_log("other type recibido", verbose)

		while window[0]!=None: 
			file.write(window.pop(0))
			rcv_base+=1
			window.append(None)

		array_numeros = [1 if x is not None else 0 for x in window]
		verbose_log(rcv_base, verbose)
		verbose_log(array_numeros, verbose)

		if done_received==True and done_seq_number == rcv_base:
			break
		else:
			data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	file.close()
	verbose_log("End receiving", verbose)







def send_ack(receiverSocket, senderAddress, p, verbose):
	if random.random() > PACKET_LOSS_PERCENTAGE:
		receiverSocket.sendto(p.to_bytes(1, 'big') + 'ACK'.encode(), senderAddress)
		verbose_log(f'ack sent: {p}', verbose)
	else:
		verbose_log(f'ack not sent: {p}', verbose)


def send_data(senderSocket, receiverAddress, data, p, verbose):
	senderSocket.sendto(data, receiverAddress)
	verbose_log(f'Sent P {p}', verbose)
	while True:
		try:
			receivedData, address = senderSocket.recvfrom(SENDER_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			verbose_log(f'{receivedData[1:].decode()} {str(i)}', verbose)
			p += 1
			return (address, p)
		except timeout:
			verbose_log(f'Timeout ocurred sending packet {p}', verbose)
			senderSocket.sendto(data, receiverAddress)
			verbose_log(f'Resending P {p}', verbose)

def recv_data(receiverSocket, verbose):
	data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	p = int.from_bytes(data[:1], 'big')
	verbose_log(f'Received packet {p}', verbose)
	type = data[1:5].decode()
	if (type == 'DONE'):
		payload = type
		return (payload, type, p, senderAddress)
	payload = data[5:]
	if (type == 'DATA'):
		return (payload, type, p, senderAddress)
	else:
		return (payload.decode(), type, p, senderAddress)

# Esto esta repetido en stop_and_wait.py
def verbose_log(message, verbose):
	if verbose:
		print(message)