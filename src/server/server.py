import socket
import threading
import uuid
import commands as cmds
import game
import json
from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import src.crypto.crypto as cp

HOST = '127.0.0.1'
PORT = 5000
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
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")  # printing the amount of threads working

            connection, address = self.server_socket.accept()  # Waiting for client to connect to server (blocking call)

            thread = threading.Thread(target=self.handle_client, args=(connection, address))
            thread.start()

    # Function that handles the clients
    def handle_client(self, conn: socket.socket, addr):
        print('[CLIENT CONNECTED] on address: ', addr)  # Printing connection address
        token = uuid.uuid4()

        self.connections[addr] = (conn,token)
        token_packet = json.dumps({"token": token})
        conn.send(cp.encrypt(token_packet))

        while True:
            try:
                cmd = cp.decrypt(conn.recv(4096))
                packet = json.loads(cmd)

                sendall = False
                if packet["token"] != self.connections[addr][1]:
                    break
                req = packet["req"]
                # login
                if req == "login":
                    to_send = cmds.Commands(self).login(req)
                # sign up
                elif req == "signup":
                    to_send = cmds.Commands(self).signup(req)
                # new game
                elif req == "new_game":
                    to_send = cmds.Commands(self).new_game(req)
                # list available games
                elif req[0] == "aval_games":
                    to_send = cmds.Commands(self).aval_games(req)
                # req to join game
                elif req[0] == "join_game":
                    to_send = cmds.Commands(self).join_game(req,conn)
                # ask to spec game
                elif req[0] == "spec":
                    to_send = cmds.Commands(self).spec_game(req,conn)
                # players makes a move
                elif req[0] == "move":
                    to_send = cmds.Commands(self).move(req)
                    sendall = True
                    g : game.Game = self.games[req["data"]["game_id"]]
                # respond to client/s
                if not sendall: conn.send(cp.encrypt(to_send))
                else:
                    all = list(g.players.values())
                    all.append(g.spectators)
                    for conn in all:
                        conn.send(cp.encrypt(to_send))
            except:
                print("[CLIENT CONNECTION INTERRUPTED] on address: ", addr)


if __name__ == '__main__':
    server = Server(HOST, PORT)
    
    print("[STARTING] server is starting...")
    server.start_server()

    print("THE END!")

