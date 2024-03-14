import socket
import json
from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import src.crypto.crypto as cp

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8080  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

class Client():
    def __init__(self, callback):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callback = callback
        self.token = 0
        self.username = ''

    def start_client(self):
        self.client_socket.connect((HOST, PORT))  # Connecting to server's socket
        print("Connecting")
        packet = json.loads(cp.decrypt(self.client_socket.recv(4096)))
        print(packet)
        self.callback(packet)

    def close_client(self):
        self.client_socket.close()

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
            packet["data"] = {"game_id": argv[0], "spec": argv[1]}
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