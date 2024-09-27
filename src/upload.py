from sys import argv
from lib.stop_and_wait import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000
FILENAME = argv[1]
SOURCE_FILEPATH = 'files/' + FILENAME

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
p = 0
type = 'FILE'
filename_len = len(FILENAME).to_bytes(1, 'big')
data = p.to_bytes(1, 'big') + type.encode() + filename_len + FILENAME.encode()
serverAddress, p = send_data(clientSocket, (SERVER_HOST, SERVER_PORT), data, p)
send_file(clientSocket, serverAddress, SOURCE_FILEPATH, p)

send_close(clientSocket, serverAddress, p)
clientSocket.close()