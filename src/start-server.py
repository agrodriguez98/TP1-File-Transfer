import queue
import socket
import threading

SERVER_HOST = 'localhost'
SERVER_PORT = 12000

CLIENT_BUFFER_SIZE = 4096
SERVER_BUFFER_SIZE = CLIENT_BUFFER_SIZE + 1 + 4 + 8
# que es el 1 y 4 ?
# arreglar esto

def send_data(serverSocket, clientAddress, data, p):
	serverSocket.sendto(data, clientAddress)
	print('Sent P', p)
	while True:
		try:
			receivedData, address = serverSocket.recvfrom(CLIENT_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			p += 1
			return (address, p)
		except socket.timeout:
			print('Timeout ocurred sending packet', p)
			serverSocket.sendto(data, clientAddress)
			print('Resending P', p)

def recv_data(serverSocket):
	data, clientAddress = serverSocket.recvfrom(SERVER_BUFFER_SIZE)
	p = int.from_bytes(data[:1], 'big')
	print('Received P', p)
	type = data[1:5].decode()
	if (type == 'DONE'):
		payload = type
		return (payload, type, p, clientAddress)
	payload = data[5:]
	if (type == 'DATA'):
		return (payload, type, p, clientAddress)
	else:
		return (payload.decode(), type, p, clientAddress)

def send_ack(serverSocket, clientAddress, p):
	serverSocket.sendto(p.to_bytes(1, 'big') + 'ACK'.encode(), clientAddress)
	print('Sent ACK', p)

def send_close(serverSocket, clientAddress, p):
	tries = 0
	data = p.to_bytes(1, 'big') + 'DONE'.encode()
	while tries < 10:
		try:
			serverSocket.sendto(data, clientAddress)
			print('Sending DONE', p)
			receivedData, address = serverSocket.recvfrom(CLIENT_BUFFER_SIZE)
			i = int.from_bytes(receivedData[:1], 'big')
			print(receivedData[1:].decode() + ' ' + str(i))
			print('Ending gracefully')
			return
		except socket.timeout:
			tries += 1
	print('Ending doubtfully')

def handle_upload(server_socket, client_address, filename, payload, p):
	# Abre o crea un archivo donde se almacenarán los datos recibidos
	# aca se puede chequear si el header es correcto?
	if payload != None:
		with open('server_storage/' + filename, 'ab') as f:
			
			f.write(payload)  # Escribe el contenido binario en el archivo

		print(f"Recibido paquete {p} de {client_address} con {len(payload)} bytes")
    
    # Enviar ACK al cliente para confirmar recepción
	send_ack(server_socket, client_address, p)

def download(serverSocket, clientAddress, filename, type):
	path = 'server_storage/' + filename
	p = 0
	with open(path, 'rb') as file:
		bytesRead = file.read(CLIENT_BUFFER_SIZE)
		while bytesRead:
			data = p.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
			clientAddress, p = send_data(serverSocket, clientAddress, data, p)
			bytesRead = file.read(CLIENT_BUFFER_SIZE)
	send_close(serverSocket, clientAddress, p)


def parse_data(data):
	p = 0
	p = int.from_bytes(data[:1], 'big')
	type = data[1:5].decode()
	filename = data[5:13].decode()
	print('Received P - ', p, type, filename)
	payload = None
	if (type == 'DATA'):
		payload = data[13:]
	return payload, filename, type, p
	


# Función que maneja cada cliente de manera concurrente
def handle_client(client_address, server_socket):
    print(f"[INFO] Iniciando manejo para el cliente: {client_address}")
    i=1
    while True:
        try:
            print("aca {}",i)
            data = clients[client_address]["data_queue"].get(timeout=1)

            # Aquí se procesaría el paquete y se manejaría la lógica de Upload o Download
            payload, filename, msg_type, p = parse_data(data)
            
            if msg_type == 'FILE' or msg_type == 'DATA':
                handle_upload(server_socket, client_address, filename, payload, p)
            elif msg_type == 'DOWNLOAD':
                handle_download(server_socket, client_address, payload, p)
            elif msg_type == 'DONE':
                print(f"[INFO] Cliente {client_address} ha terminado la transferencia.")
                send_ack(server_socket, client_address, p)
                break
        except queue.Empty:
            continue
        except Exception as e:
            print(f"[ERROR] Error con el cliente {client_address}: {e}")
            break
		
        i += 1

    # Limpieza: eliminar el cliente del diccionario
    with clients_lock:
        if client_address in clients:
            del clients[client_address]
    print(f"[INFO] Finalizando manejo para el cliente: {client_address}")


##################
# Diccionario para almacenar los hilos activos y clientes
clients = {}

# Bloqueo para asegurar acceso sincronizado al diccionario de clientes
clients_lock = threading.Lock()
# Crear socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))

print(f"[INFO] Servidor escuchando en {SERVER_HOST}:{SERVER_PORT}")

while True:
	# Recibir datos de cualquier cliente
	data, client_address = server_socket.recvfrom(SERVER_BUFFER_SIZE)
	
	# Bloqueo para acceso seguro al diccionario de clientes
	with clients_lock:
		# Si el cliente no ha sido manejado antes, crear un nuevo hilo
		if client_address not in clients:
			print(f"[INFO] Nueva conexión desde {client_address}")
			# Crear cola para almacenar mensajes del cliente
			clients[client_address] = {"data_queue": queue.Queue()}
			
			# Crear un hilo para manejar ese cliente
			client_thread = threading.Thread(target=handle_client, args=(client_address, server_socket))
			clients[client_address]["thread"] = client_thread
			client_thread.start()
		
	# Agregar el mensaje a la cola del cliente correspondiente
	clients[client_address]["data_queue"].put(data)