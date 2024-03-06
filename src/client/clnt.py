import socket
import json
import time

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

    def start_client(self):
        self.client_socket.connect((HOST, PORT))  # Connecting to server's socket
        print("Connecting")
        self.token = self.client_socket.recv(4096)
        self.token = self.token.decode(FORMAT)
        print(self.token)

    def close_client(self):
        self.client_socket.close()

    def request(self,req, *argv):
        data = "{} {}".format(self.token, req)
        if req in ["move"]:
            data = data + " {} {}".format(self.token, req, argv[0], argv[1], argv[2])
        elif req in ["login", "signup"]:
            data = data + " {} {}".format(self.token, req, argv[0], argv[1])
        elif req == ["new", "join", "spec"]: 
            data = data + " {} {}".format(self.token, req, argv[0]) # num players / game id
        
        self.client_socket.send(data.encode(FORMAT))
        time.sleep(0.05)
        self.recvd_data = self.client_socket.recv(4096).decode(FORMAT)
   

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
