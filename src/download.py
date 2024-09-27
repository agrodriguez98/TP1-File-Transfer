from socket import *
from sys import argv
from time import sleep
from lib.stop_and_wait import *
import argparse

def create_download_parser():
    parser = argparse.ArgumentParser(description="Download a file from the server")
        
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
    parser.add_argument('-d', '--dst', type=str, required=True,
                        help="destination file path")
    parser.add_argument('-n', '--name', type=str, required=True,
                        help="file name")
    return parser

parser = create_download_parser()
args = parser.parse_args()

if args.verbose:
    print("Verbose mode enabled")
    print(f"Server IP: {args.host}")
    print(f"Server Port: {args.port}")
    print(f"Destination file path: {args.dst}")
    print(f"File name: {args.name}")
    

receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.settimeout(1)
senderAddress = (args.host, args.port)
counter = 0
send_download_request(receiverSocket, senderAddress, args.name, counter, args.verbose)
dst_filepath = args.dst + '/' + args.name
recv_file(receiverSocket, senderAddress, dst_filepath, type, args.verbose)

verbose_log('Done receiving', args.verbose)