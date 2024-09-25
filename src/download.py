from lib.stop_and_wait import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000
FILENAME = 'JWT.png'
DESTINATION_FILEPATH = 'files/' + FILENAME
	
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
p = 0
type = 'DOWN'
data = p.to_bytes(1, 'big') + type.encode() + FILENAME.encode()
serverAddress, p = send_data(clientSocket, (SERVER_HOST, SERVER_PORT), data, p)
recv_file(clientSocket, serverAddress, DESTINATION_FILEPATH, type)
clientSocket.close()