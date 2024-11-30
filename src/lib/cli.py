from argparse import ArgumentParser
from pathlib import Path
from enum import Enum
import ipaddress

SERVICE_HOST = 'localhost'
SERVICE_PORT = 12000
STORAGE_DIRPATH = './server_storage'
SR_MODE = False

FILENAME = 'JWT.png'
DESTINATION_FILEPATH = './files'
FILENAME = 'AUTH.png'
SOURCE_FILEPATH = './files'

class App(Enum):
    SERVER = 1
    CLIENT_DOWNLOAD = 2
    CLIENT_UPLOAD = 3

def get_argparser(app):
    argparser = ArgumentParser()

    group = argparser.add_mutually_exclusive_group(required=False)
    group.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    group.add_argument("-q", "--quiet", action="store_true", help="decrease output verbosity")
    argparser.add_argument("-H", "--host", action="store", type=str, nargs="?", default=SERVICE_HOST, help="service IP address (default: %(default)s)")
    argparser.add_argument("-p", "--port", action="store", type=int, nargs="?", default=SERVICE_PORT, help="service port (default: %(default)s)")
    argparser.add_argument("-sr", "--modesr", action="store_true", default=SR_MODE, help="defines if the mode is stop & wait or selective repeat (default: stop & wait)")

    if app == App.SERVER:
        argparser.add_argument("-s", "--storage", action="store", type=str, nargs="?", default=STORAGE_DIRPATH, help="storage dir path (default: %(default)s)")

        return argparser
    
    if app == App.CLIENT_UPLOAD:
            argparser.add_argument("-s", "--src", action="store", type=str, nargs="?", default=SOURCE_FILEPATH, help="source file path (default: %(default)s)")

    if app == App.CLIENT_DOWNLOAD:
            argparser.add_argument("-d", "--dst", action="store", type=str, nargs="?", default=DESTINATION_FILEPATH, help="destination file path (default: %(default)s)")

    argparser.add_argument("-n", "--name", action="store", type=str, nargs="?", help="file name", required=True)

    return argparser

def get_args(argparser, app):
    args = argparser.parse_args()

    if not is_valid_ip_address(args.host):
        argparser.exit(1, message="ERROR: The IP address is not valid\n")

    if not is_valid_port(args.port):
        argparser.exit(1, message="ERROR: The port is not valid\n")

    if app == App.SERVER:
        if not Path(args.storage).exists():
            argparser.exit(1, message="ERROR: The storage directory path doesn't exist\n")

    elif app == App.CLIENT_UPLOAD:
        if not Path(args.src).exists():
            argparser.exit(1, message="ERROR: The source file path doesn't exist\n")
        if not Path(args.src + '/' + args.name).exists():
            argparser.exit(1, message=f"ERROR: The file {args.name} doesn't exist\n")

    else:
        if not Path(args.dst).exists():
            argparser.exit(1, message="ERROR: The destination file path doesn't exist\n")
        if Path(args.dst + '/' + args.name).exists():
            argparser.exit(1, message=f"ERROR: A file named {args.name} already exists\n")

    return args

def is_valid_ip_address(address):
    try:
        if address == SERVICE_HOST:
            pass
        else:
            ipaddress.ip_address(address)
        return True
    except ValueError:
        return False
    
def is_valid_port(port):
    return 1023 < port <= 65535