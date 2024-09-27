import argparse
from sys import argv
from lib.stop_and_wait import *

def create_upload_parser():
    parser = argparse.ArgumentParser(description="Upload a file to the server")
        
    # Para que sólo se pueda elegir uno
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true',
                       help="increase output verbosity")
    group.add_argument('-q', '--quiet', action='store_true',
                       help="decrease output verbosity")
    parser.add_argument('-H', '--host', type=str, default='localhost',
                        help="server IP address (default: localhost)")
    parser.add_argument('-p', '--port', type=int, default=12000,
                        help="server port (default: 12000)")
    parser.add_argument('-s', '--src', type=str, required=True,
                        help="source file path")
    parser.add_argument('-n', '--name', type=str, required=True,
                        help="file name")
    return parser

parser = create_upload_parser()
args = parser.parse_args()

if args.verbose:
    print("Verbose mode enabled")
    print(f"Server IP: {args.host}")
    print(f"Server Port: {args.port}")
    print(f"Source file path: {args.src}")
    print(f"File name: {args.name}")


clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
p = 0
serverAddress = (args.host, args.port)

p = send_upload_request(clientSocket, serverAddress, args.name, p, args.verbose)

src_filepath = args.src + '/' + args.name
send_file(clientSocket, serverAddress, src_filepath, p, args.verbose)
send_close(clientSocket, serverAddress, p, args.verbose)
clientSocket.close()