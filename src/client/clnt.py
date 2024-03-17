import socket
import json
from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import src.crypto.crypto as cp

"""
Client class for representing client connection
"""
class Client():
    """
    Constructor for Client.
    param callback: callback method to call after receiving packet
    param host: the server IP
    param port: the server port
    """
    def __init__(self, callback, host, port):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callback = callback
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.token = 0
        self.username = ''

    """
    Start up the client (connect to the server)
    """
    def start_client(self):
        self.client_socket.connect((self.host, self.port))  # Connecting to server's socket
        print("Connecting")
        packet = json.loads(cp.decrypt(self.client_socket.recv(4096)))
        self.callback(packet)

    """
    Close client connection.
    """
    def close_client(self):
        self.client_socket.close()

    """
    Make a server request
    param req: the request to make to the server
    param argv: the rest of the data for the request
    """
    def request(self, req, *argv):
        packet = {
            "token": self.token,
            "req": req,
            "data": None,
        }
        if req in ["move"]:
            packet["data"] = {"game_id": argv[0], "i": argv[1], "j": argv[2]}
        elif req in ["login", "signup"]:
            packet["data"] = {"username": argv[0], "password": argv[1]}
        elif req in ["exit_game"]:
            packet["data"] = {"game_id": argv[0], "spec": argv[1] ,"destroy": argv[2]}
        elif req in ["join", "spec", "turn_ended", "timer"]:
            packet["data"] = {"game_id": int(argv[0])} # arg - game_id
        elif req in ["new"]:
            packet["data"] = {"num_players": argv[0]} # arg - num_players
        elif req == "update":
            packet["data"] = {"game_id": argv[0]}
        elif req in ["lb", "aval", "exit", "logout"]:
            packet.pop("data") # no args or data needed
            print(packet)
        self.client_socket.send(cp.encrypt(json.dumps(packet,default=list)))
        response = json.loads(cp.decrypt(self.client_socket.recv(4096)))
        self.callback(response)