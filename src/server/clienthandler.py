import threading
import socket
import json
import commands as cmds
from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import src.crypto.crypto as cp
import src.server.game as game

class ClientHandler(threading.Thread):
    def __init__(self, server ,conn: socket.socket, addr):
        super().__init__()
        self.server = server
        self.conn : socket.socket = conn
        self.addr = addr
        self.username = ''

    def run(self):
        print('[CLIENT CONNECTED] on address: ', self.addr)  # Printing connection address
        self.server.connections[self.addr] = self.conn

        self.conn.send(cp.encrypt(cmds.Data("suc", "connected")))

        while True:
            try:
                recv = cp.decrypt(conn.recv(4096))
                packet = json.loads(recv)
                cmd = cmds.Commands(self.server)
                req = packet["req"]
                sendall = False

                # validate token (on login the client doesn't have token yet)
                if req != "login" or not cmd.valid_token(req["token"]):
                    to_send = cmds.Data("err", "invalid_token")
                # login
                elif req == "login":
                    to_send = cmd.login(req)
                # sign up
                elif req == "signup":
                    to_send = cmd.signup(req)
                # new game
                elif req == "new_game":
                    to_send = cmd.new_game(req)
                # list available games
                elif req[0] == "aval_games":
                    to_send = cmd.aval_games(req)
                # req to join game
                elif req[0] == "join_game":
                    to_send = cmd.join_game(req,conn)
                # ask to spec game
                elif req[0] == "spec":
                    to_send = cmd.spec_game(req,conn)
                # players makes a move
                elif req[0] == "move":
                    to_send = cmd.move(req)
                    sendall = True
                    g : game.Game = self.server.games[req["data"]["game_id"]]
                # respond to client/s
                if not sendall: self.conn.send(cp.encrypt(to_send))
                else:
                    all : list[socket.socket] = list(g.players.values()) 
                    all.append(g.spectators)
                    for conn in all:
                        conn.send(cp.encrypt(to_send))
            except:
                print("[CLIENT CONNECTION INTERRUPTED] on address: ", self.addr)