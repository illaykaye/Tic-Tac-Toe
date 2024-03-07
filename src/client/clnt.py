import socket
import json
import time
import src.crypto.crypto as cp

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

class Client():
    def __init__(self):
        IP = socket.gethostbyname(socket.gethostname())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvd_data = ""
        self.token = 0
        self.game_id = None

    def start_client(self):
        self.client_socket.connect((HOST, PORT))  # Connecting to server's socket
        print("Connecting")
        self.token = cp.decrypt(self.client_socket.recv(1024))
        print(self.token)

    def close_client(self):
        self.client_socket.close()

    def request(self,req, *argv):
        packet = {
            "token": self.token,
            "req": req,
            "data": None,
            "timestamp": time.time()
        }
        if req in ["move"]:
            packet["data"] = {"game_id": self.game_id, "i": argv[0], "j": argv[1]}
            #data = data + " {} {}".format(self.token, req, argv[0], argv[1], argv[2])
        elif req in ["login", "signup"]:
            packet["data"] = {"username": argv[0], "password": argv[1]}
            #data = data + " {} {}".format(self.token, req, argv[0], argv[1])
        elif req in ["new", "join", "spec"]:
            packet["data"] = {"game_id", argv[0]}
            data = data + " {} {}".format(self.token, req, argv[0]) # num players / game id
        elif req in ["lb", "aval"]:
            packet.pop("data")

        self.client_socket.send(cp.encrypt(json.dump(packet)))
        time.sleep(0.05)
        self.recvd_data = cp.decrypt(self.client_socket.recv(4096))
   

    def leaderboard(self):
        self.client_socket.send("leaderboard".encode(FORMAT))
        response = self.client_socket.recv(4096).decode(FORMAT)
        return json.loads(response)
    
    def available_games(self):
        self.client_socket.send("aval_games".encode(FORMAT))
        response = self.client_socket.recv(4096)
        return json.loads(response)

    def new_game(self):
        return 0

    def join_game(self, game_id):
        self.client_socket.send("join {}".format(game_id).encode(FORMAT))

    def exit_game(self):
        return 0
