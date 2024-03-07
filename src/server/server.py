import socket
import threading
import time
import uuid
import commands as cmds
import game
import json
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

        self.data_hazard = False
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
        username = ""
        self.connections[addr] = (conn,token)
        conn.send("{}".format(token).encode(FORMAT))

        while True:
            try:
                cmd = cp.decrypt(conn.recv(4096))
                req = cmd.split(" ")
                sendall = False
                if req[0] != self.connections[addr][1]:
                    break
                req = req[1::]
                # login
                if req[0] == "login":
                    if cmds.login(req):
                        data = "logged"
                        username = req[1]
                    else: 
                        data = "not_found"

                # sign up
                elif req[0] == "signup":
                    if cmds.signup(req):
                        data = "signed_up"
                    else:
                        data = "usr_unavl"

                # new game
                elif req[0] == "new_game":
                    game_id = len(self.games)
                    self.games.append(cmds.new_game(req,game_id))
                    data = "crtd_gm {}".format(game_id)

                # list available games
                elif req[0] == "aval_games":
                    data = cmds.aval_games(self.games)

                # req to join game
                elif req[0] == "join_game":
                    id = cmds.join_game(req)
                    if id > 0:
                        data = "jnd_gm {}".format(id)
                    else:
                        data = "unable_jn"

                # ask to spec game
                elif req[0] == "spec":
                    g : game.Game = self.games[int(req[1])]
                    g.add_spectator(conn)
                    data = "spec_succ {} {}".format(g.id, g.board)

                # players makes a move
                elif req[0] == "move":
                    g : game.Game = self.games[int(req[1])]
                    g.move(req[2],req[3])
                    data = "board {}".format(json.dump(g.board))

                # respond to client/s
                if not sendall: conn.send(cp.encrypt(data))
                else:
                    all = list(g.players.values())
                    all.append(g.spectators)
                    for conn in all:
                        conn.send(cp.encrypt(data))
            except:
                print("[CLIENT CONNECTION INTERRUPTED] on address: ", addr)


if __name__ == '__main__':
    server = Server(HOST, PORT)
    
    print("[STARTING] server is starting...")
    server.start_server()

    print("THE END!")

