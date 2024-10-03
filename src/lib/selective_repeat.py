from socket import *
from datetime import datetime
import time
import random
import bisect

random.seed() 

SENDER_BUFFER_SIZE = 8000
PACKET_NUMBER_BYTES = 2
TYPE_BYTES = 4
RECEIVER_BUFFER_SIZE = SENDER_BUFFER_SIZE + PACKET_NUMBER_BYTES + TYPE_BYTES
WINDOW_SIZE = 10

TIMEOUT = 0.3
PACKET_LOSS_PERCENTAGE = 0

WINDOW_PERCENTAGE = 0.7
ACK_DELAY = 0.1


SENDER_TIMEOUT = 0.09

#
# Sender role
#
def send_file(senderSocket, receiverAddress, filepath, seq_number, verbose):
	print("yeah, modesr on")
	bool_window= [False]*WINDOW_SIZE
	time.sleep(0.1)
	senderSocket.setblocking(False)
	window = []
	send_base = seq_number
	file = open(filepath, 'rb')
	bytesRead = file.read(SENDER_BUFFER_SIZE)
	endparse = False
	while bytesRead or len(window) > 0:

		#verbose_log(send_base, verbose)
		#array_numeros = [int(b) for b in bool_window]
		#verbose_log(array_numeros, verbose)
		#print(len(window))
		if seq_number < send_base + WINDOW_SIZE and bytesRead:
			data = seq_number.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'DATA'.encode() + bytesRead
		
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
				#seq_number_ack = int.from_bytes(receivedData[:PACKET_NUMBER_BYTES], 'big')# old version
				hands_deserialized = []
				number_ammount = int.from_bytes(receivedData[:PACKET_NUMBER_BYTES], 'big')
				print(number_ammount)
				payload = receivedData[PACKET_NUMBER_BYTES + TYPE_BYTES:PACKET_NUMBER_BYTES + TYPE_BYTES+number_ammount*PACKET_NUMBER_BYTES]

				for i in range(0, len(payload), 2 * PACKET_NUMBER_BYTES):
					first_number = int.from_bytes(payload[i:i + PACKET_NUMBER_BYTES], 'big')
					second_number = int.from_bytes(payload[i + PACKET_NUMBER_BYTES:i + 2 * PACKET_NUMBER_BYTES], 'big')
					hands_deserialized.append((first_number, second_number))
				print("received this:"+str(hands_deserialized))
				for hand in hands_deserialized:
					for seq_number_ack in range(hand[0], hand[1]+1):
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
					print("packet resent: ",str(i+send_base))
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
			data = seq_number.to_bytes(PACKET_NUMBER_BYTES, 'big') + type.encode()
			if random.random() > PACKET_LOSS_PERCENTAGE:
				senderSocket.sendto(data, receiverAddress)
			seq_number+=1
			#window.append((data, seq_number, time.time() + TIMEOUT))

#
# Receiver role
#
def recv_file(receiverSocket, senderAddress, filepath, type, seq_number, verbose):
	print("receiving file")
	time.sleep(0.01)
	window= [None]*WINDOW_SIZE
	file = open(filepath, 'wb')
	rcv_base = seq_number
	done_received = False
	to_acknowledge = []
	last_time = time.time()
	receiverSocket.setblocking(False)
	
	while True:

		if (len(to_acknowledge) > 0 and time.time() > last_time+ACK_DELAY) or len(to_acknowledge)>WINDOW_SIZE*WINDOW_PERCENTAGE:
			print("tiempoo")
			last_time=time.time()
			send_sack(to_acknowledge, receiverSocket, senderAddress, verbose)
			to_acknowledge = []
		try:
			data, senderAddress = receiverSocket.recvfrom(RECEIVER_BUFFER_SIZE)
			

			seq_number = int.from_bytes(data[:PACKET_NUMBER_BYTES], 'big')
			type = data[PACKET_NUMBER_BYTES:PACKET_NUMBER_BYTES + TYPE_BYTES].decode()
			if (type == 'DONE'):
				
				verbose_log("DONE", verbose)
				done_seq_number = seq_number
				done_received = True
				verbose_log(f'{rcv_base} {done_seq_number}', verbose)
				bisect.insort(to_acknowledge, seq_number)

			elif(type == 'DATA'):
				payload = data[PACKET_NUMBER_BYTES + TYPE_BYTES:]
				if seq_number < rcv_base:
					bisect.insort(to_acknowledge, seq_number)
					verbose_log("repeated", verbose)

				elif seq_number < rcv_base + WINDOW_SIZE:
					bisect.insort(to_acknowledge, seq_number)
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
		except:
			pass

	file.close()
	verbose_log("End receiving", verbose)

def send_sack(to_acknowledge, receiverSocket, senderAddress, verbose):
	print(to_acknowledge)
	hands = []
	hands.append((None, None))
	for seq_number in to_acknowledge:
		if hands[len(hands)-1][0] == None:
			hands[len(hands)-1] = (seq_number, seq_number)
		elif hands[len(hands)-1][1] + 1 == seq_number or hands[len(hands)-1][1] == seq_number:
			hands[len(hands)-1] = (hands[len(hands)-1][0], seq_number)
		else:
			hands.append((None, None))
			hands[len(hands)-1] = (seq_number, seq_number)
	hands_serialized = []
	for hand in hands:
		hands_serialized.append(hand[0].to_bytes(PACKET_NUMBER_BYTES, 'big'))
		hands_serialized.append(hand[1].to_bytes(PACKET_NUMBER_BYTES, 'big'))
	sack_message_seq_number = 0
	data = (2*len(hands)).to_bytes(PACKET_NUMBER_BYTES, 'big')+ 'SACK'.encode() + b''.join(hands_serialized)
	to_acknowledge = []
	print(hands)
	if random.random() > PACKET_LOSS_PERCENTAGE:
		receiverSocket.sendto(data, senderAddress)
		verbose_log(f'ack sent{hands}', verbose)
	else:
		verbose_log(f'ack not sent: {hands}', verbose)


def send_ack(receiverSocket, senderAddress, p, verbose):
	if random.random() > PACKET_LOSS_PERCENTAGE:
		receiverSocket.sendto(p.to_bytes(PACKET_NUMBER_BYTES, 'big') + 'ACKN'.encode(), senderAddress)
		verbose_log(f'Sent ACK {p}', verbose)
	else:
		verbose_log(f'/Not sent ACK: {p}', verbose)




def send_data(senderSocket, receiverAddress, data, p, verbose):
	senderSocket.sendto(data, receiverAddress)
	tries = 0
	verbose_log(f'Sent packet {p}', verbose)
	while tries < SENDER_TRIES:
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
	verbose_log(f'Attempted to send data {SENDER_TRIES} times and got no answer', verbose)
	senderSocket.close()
	exit(1)

def recv_data(receiverSocket, verbose):
	try:
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
	except timeout:
		verbose_log(f'Connection dropped unexpectedly', verbose)
		raise Exception("Connection dropped unexpectedly")

# Esto esta repetido en stop_and_wait.py
def verbose_log(message, verbose):
	if verbose:
		print(message)

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
