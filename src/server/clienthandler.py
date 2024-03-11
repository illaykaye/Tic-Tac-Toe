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
        self.broadcast = False

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
                cmd = cmds.Commands(self, self.server)
                req = packet["req"]
                to_self = None
                # validate token (on login the client doesn't have token yet)
                '''if req not in ["signup", "login"] and not cmd.valid_token(req["token"]):
                    to_send = cmds.Data("err", "invalid_token")'''
                # login
                if req == "exit":
                    self.server.connections.pop(self.addr)
                    if self.in_game:
                        self.games[self.game_id].players.pop(self.username)
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
                    to_send, to_self ,clients = cmd.join_game(packet["data"],self.conn,self.username) # to_send would be to all other client, to_self to the client who sent the request
                # ask to spec game
                elif req == "spec":
                    to_send = cmd.spec_game(packet["data"],self.conn)
                elif req == "exit_game":
                    to_send, clients = cmd.exit_game(packet["data"],self.conn)
                # players makes a move
                elif req == "move":
                    to_send, clients = cmd.move(packet["data"],self.username)
                # respond to client/s
                print(to_send)
                if self.broadcast: # broadcast to all (or almost all) clients in game
                    if clients != None:
                        for conn in clients: conn.send(cp.encrypt(to_send))
                    if to_self != None: self.conn.send(cp.encrypt(to_self))
                else:
                    self.conn.send(cp.encrypt(to_send))
                self.broadcast = False
        except socket.timeout:
            print("Connection with {} timed out.".format(self.addr))
        except Exception as e:
            print("An error occured with {}: {}".format(self.addr, e))
        finally:
            self.server.connections.pop(self.addr)
            self.conn.close()
            print("Connection with {} closed.".format(self.addr))