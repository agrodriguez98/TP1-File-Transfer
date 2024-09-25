from lib.stop_and_wait import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000
FILENAME = 'AUTH.png'
SOURCE_FILEPATH = 'files/' + FILENAME

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
p = 0
type = 'FILE'
data = p.to_bytes(1, 'big') + type.encode() + FILENAME.encode()
serverAddress, p = send_data(clientSocket, (SERVER_HOST, SERVER_PORT), data, p)
send_file(clientSocket, serverAddress, SOURCE_FILEPATH, p)
clientSocket.close()