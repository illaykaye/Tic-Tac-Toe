import socket
import json
import time
import threading
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

    def listen(self):
        response = json.loads(cp.decrypt(self.client_socket.recv(4096)))
        print(response)
        self.callback(response)

    def request(self,req, *argv):
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
            packet["data"] = {"mode": argv[0], "game_id": argv[1]}
        elif req in ["join", "spec", "timesup"]:
            packet["data"] = {"game_id": int(argv[0])} # arg - game_id
        elif req in ["new"]:
            packet["data"] = {"num_players": argv[0]} # arg - num_players
        elif req == "update":
            packet["data"] = {"game_id": argv[0]}
        elif req == "exit_game":
            packet["data"] = {"game_id": argv[0], "spec": argv[1]}
        elif req in ["lb", "aval"]:
            packet.pop("data") # no args or data needed
        self.client_socket.send(cp.encrypt(json.dumps(packet,default=list)))
        #time.sleep(0.2)
        response = json.loads(cp.decrypt(self.client_socket.recv(4096)))
        print(response)
        self.callback(response)

class TimerHandler(threading.Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """

    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()