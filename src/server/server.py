import socket
import threading
import clienthandler as ch
from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

HOST = '127.0.0.1'
PORT = 8080
FORMAT = 'utf-8'
ADDR = (HOST, PORT)


class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)

        self.data_hazard = {"users": False, "leader": False}
        self.connections = {}
        self.games = []

        self.IP = socket.gethostbyname(socket.gethostname())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Function that starts the server
    def start_server(self):
        self.server_socket.bind(ADDR)  # binding socket with specified IP+PORT tuple

        print(f"[LISTENING] server is listening on {HOST}")
        self.server_socket.listen()  # Server is open for connections

        while True:
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n")  # printing the amount of threads working

            connection, address = self.server_socket.accept()  # Waiting for client to connect to server (blocking call)

            thread = threading.Thread(target=ch.ClientHandler, args=(connection, address))
            thread.start()

if __name__ == '__main__':
    server = Server(HOST, PORT)
    
    print("[STARTING] server is starting...")
    server.start_server()

    print("THE END!")

