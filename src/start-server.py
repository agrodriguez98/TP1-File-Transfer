import queue
import socket
import threading
from lib.stop_and_wait import *

SERVICE_HOST = 'localhost'
SERVICE_PORT = 12000
STORAGE_DIRPATH = './server_storage'

# Esto tiene que estar igual que en donwload.py
# Habria que unificarlo en un solo lugar

# El tamaño de p creo que hay que agrandarlo para soportar archivos mas grandes

def handle_upload(server_socket, client_address, filename, payload, p):
	# Abre o crea un archivo donde se almacenarán los datos recibidos
	# aca se puede chequear si el header es correcto?
	if payload != None:
		path = STORAGE_DIRPATH + '/' + filename
		with open(path, 'ab') as f:
			f.write(payload)  # Escribe el contenido binario en el archivo
		print(f"Recibido paquete {p} de {client_address} con {len(payload)} bytes")
    
    # Enviar ACK al cliente para confirmar recepción
	send_ack(server_socket, client_address, p)

def handle_download(serverSocket, clientAddress, filename, p, offset):
	done = False
	path = STORAGE_DIRPATH + '/' + filename
	with open(path, 'rb') as file:
		file.seek(offset)
		bytesRead = file.read(SENDER_BUFFER_SIZE)
		if bytesRead:
			data = p.to_bytes(1, 'big') + 'DATA'.encode() + bytesRead
			serverSocket.sendto(data, client_address)
			print(f"Enviado fragmento desde offset {offset} al cliente {client_address}, p: {p}")
			p += 1
			offset = offset + len(bytesRead)
		else:
			print(f"El archivo {filename} fue completamente enviado.")
			data = p.to_bytes(1, 'big') + 'DONE'.encode()
			serverSocket.sendto(data, clientAddress)
			done = True
		return offset, p, done


def parse_data(data):
	p = 0
	p = int.from_bytes(data[:1], 'big')
	type = data[1:5].decode()
	if (type == 'ACK1'):
		return None, None, 'ACK1', p
	filename = None
	payload = None
	if (type == 'DATA'):
		payload = data[5:]
		print('Received P - '+ str(p) +' - ' + type + ' - size: ' + str(len(payload)))

	if type == 'FILE' or type == 'DOWN':
		filename_len = int.from_bytes(data[5:6], 'big')
		filename = data[6 : 6 + filename_len].decode()
		print('Received P - ', p, type, filename)
	return payload, filename, type, p

# Función que maneja cada cliente de manera concurrente
def handle_client(client_address, server_socket):
    # Se podría identificar en el primer mensaje el servicio que se va a utilizar
	# si es upload o download. Asi se define el comportamiento con ese cliente,
	# que no va a cambiar hasta que se cierre la conexion y el thread
    print(f"[INFO] Iniciando manejo para el cliente: {client_address}")
    i=1
    last_p_sent = 0
    done = False

	#Variables que se inicializan con el primer mensaje
    file_name = None
    offset = 0

    while True:
        try:
            data = clients[client_address]["data_queue"].get(timeout=1)

            # Aquí se procesaría el paquete y se manejaría la lógica de Upload o Download
            payload, filename, msg_type, p = parse_data(data)
            if msg_type == 'FILE' or msg_type == 'DOWN':
				# Es el mensaje que inicia la transferencia
				# Se guarda el nombre del archivo
                file_name = filename

            if msg_type == 'FILE' or msg_type == 'DATA':
                handle_upload(server_socket, client_address, file_name, payload, p)
            elif msg_type == 'DOWN':
                #file_name = filename # medio hardcodeado pero es para poder responder el ACK
                offset, last_p_sent, done = handle_download(server_socket, client_address, file_name, last_p_sent, offset)
            elif msg_type == 'DONE':
				# este done se recibe cuando se termina el upload
                print(f"[INFO] Cliente {client_address} ha terminado la transferencia.")
                send_ack(server_socket, client_address, p)
                break
            elif msg_type == 'ACK1': #esta puesto como ACK1 porque esta hardcodeado la cant de bytes
                if done:
                    break
                offset, last_p_sent, done = handle_download(server_socket, client_address, file_name, last_p_sent, offset)

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
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((SERVICE_HOST, SERVICE_PORT))

print(f"[INFO] Servidor escuchando en {SERVICE_HOST}:{SERVICE_PORT}")

while True:
	# Recibir datos de cualquier cliente
	data, client_address = server_socket.recvfrom(RECEIVER_BUFFER_SIZE)
	
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