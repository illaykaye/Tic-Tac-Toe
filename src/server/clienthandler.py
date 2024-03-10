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
    def __init__(self, server, conn: socket.socket, addr):
        threading.Thread.__init__(self)
        self.server = server
        self.conn : socket.socket = conn
        self.addr = addr
        self.username = ''
        self.in_game = False
        self.game_id = -1

    def run(self):
        print('[CLIENT CONNECTED] on address: ', self.addr)  # Printing connection address

        try:
            self.server.connections[self.addr] = self.conn
            print("connected")
            self.conn.send(cp.encrypt(cmds.Data("suc", "connected").to_json()))

            while True:
                recv = cp.decrypt(self.conn.recv(4096))
                print(recv)
                packet = json.loads(recv)
                cmd = cmds.Commands(self.server)
                req = packet["req"]
                sendall = False
                print(packet)
                # validate token (on login the client doesn't have token yet)
                '''if req not in ["signup", "login"] and not cmd.valid_token(req["token"]):
                    to_send = cmds.Data("err", "invalid_token")'''
                # login
                if req == "exit":
                    self.server.connections.pop(self.addr)
                    if self.in_game:
                        self.games[self.game_id].players.pop(self.username)
                        self.games[self.game_id].usernames.remove(self.username)
                elif req == "login":
                    to_send = cmd.login(packet["data"])
                # sign up
                elif req == "signup":
                    to_send = cmd.signup(packet["data"])
                # new game
                elif req == "new":
                    print("new game")
                    to_send = cmd.new_game(packet["data"],self.conn,self.username)
                # list available games
                elif req == "aval":
                    to_send = cmd.aval_games()
                elif req == "lb":
                    print("leaderboard")
                    to_send = cmd.leaderboard()
                # req to join game
                elif req == "join":
                    to_send = cmd.join_game(packet["data"],self.conn,self.username)
                # ask to spec game
                elif req == "spec":
                    to_send = cmd.spec_game(packet["data"],self.conn)
                # players makes a move
                elif req == "move":
                    to_send = cmd.move(req)
                    sendall = True
                    g : game.Game = self.server.games[req["data"]["game_id"]]
                # respond to client/s
                print(to_send)
                if not sendall: self.conn.send(cp.encrypt(to_send))
                else:
                    all : list[socket.socket] = list(g.players.values()) 
                    all.append(g.spectators)
                    for conn in all:
                        conn.send(cp.encrypt(to_send))
        except socket.timeout:
            print("Connection with {} timed out.".format(self.addr))
        except Exception as e:
            print("An error occured with {}: {}".format(self.addr, e))
        finally:
            self.server.connections.pop(self.addr)
            self.conn.close()
            print("Connection with {} closed.".format(self.addr))