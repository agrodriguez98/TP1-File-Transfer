from socket import *
from datetime import datetime
import time
import random
random.seed() 

SENDER_BUFFER_SIZE = 4096
PACKAGE_NUMBER_BYTES = 1
TYPE_BYTES = 4
RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKAGE_NUMBER_BYTES + TYPE_BYTES
WINDOW_SIZE = 10

TIMEOUT = 1
PACKET_LOSS_PERCENTAGE = 0.1

#
# Sender role
#
def send_file(senderSocket, receiverAddress, filepath, seq_number):

	confirmados=[]
	bool_window= [False]*WINDOW_SIZE

	senderSocket.setblocking(False)
	window = []
	send_base = seq_number
	file = open(filepath, 'rb')
	bytesRead = file.read(SENDER_BUFFER_SIZE)
	endparse = False
	while bytesRead or len(window) > 0:
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
			print(send_base)
			array_numeros = [int(b) for b in bool_window]
			print(array_numeros)
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
			print("FIN PARSEO ARCHIVO")
			type = 'DONE'
			data = seq_number.to_bytes(1, 'big') + type.encode()
			if random.random() > PACKET_LOSS_PERCENTAGE:
				senderSocket.sendto(data, receiverAddress)
			seq_number+=1
			#window.append((data, seq_number, time.time() + TIMEOUT))

#
# Receiver role
#
def recv_file(receiverSocket, senderAddress, filepath, type, seq_number):
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
			
			print("DONE")
			done_seq_number = seq_number
			done_received = True
			print(rcv_base, done_seq_number)
			
			send_ack(receiverSocket, senderAddress, seq_number)
		elif(type == 'DATA'):
			payload = data[5:]
			if seq_number < rcv_base:
				send_ack(receiverSocket, senderAddress, seq_number)
				print("repeated")

			elif seq_number < rcv_base + WINDOW_SIZE:
				send_ack(receiverSocket, senderAddress, seq_number)
				window[seq_number-rcv_base]=payload

			else:
				print("out of window")
		else:
			print("other type recibido")

		while window[0]!=None: 
			file.write(window.pop(0))
			rcv_base+=1
			window.append(None)

		array_numeros = [1 if x is not None else 0 for x in window]
		print(rcv_base)
		print(array_numeros)

		if done_received==True and done_seq_number == rcv_base:
			break
		else:
			data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
	file.close()
	print("End receiving")







def send_ack(receiverSocket, senderAddress, p):
	if random.random() > PACKET_LOSS_PERCENTAGE:
		receiverSocket.sendto(p.to_bytes(1, 'big') + 'ACK'.encode(), senderAddress)
		print("ack sent: "+str(p))
	else:
		print("ack not sent: "+str(p))


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