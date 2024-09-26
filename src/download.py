from socket import *
from sys import argv
from time import sleep
from lib.stop_and_wait import *

SERVER_HOST = 'localhost'
SERVER_PORT = 12000

BUFFER_SIZE = 4096
SERVER_BUFFER_SIZE = BUFFER_SIZE + 1 + 4 + 8

FILENAME = argv[1]
DESTINATION_FILEPATH = 'files/' + FILENAME
# El tamaño del filename esta hardcodeado en 8 bytes
# después hay que mejorarlo

receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.settimeout(1)
senderAddress = (SERVER_HOST, SERVER_PORT)
counter = 0
send_file_request(receiverSocket, senderAddress, FILENAME, counter)
recv_file(receiverSocket, senderAddress, DESTINATION_FILEPATH, type)

print('Done receiving')