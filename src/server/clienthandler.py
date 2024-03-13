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

    def run(self):
        print('[CLIENT CONNECTED] on address: ', self.addr)  # Printing connection address

        try:
            self.server.connections[self.addr] = self
            self.conn.send(cp.encrypt(cmds.Data("suc", "connected").to_json()))

            while True:
                recv = cp.decrypt(self.conn.recv(4096))
                packet = json.loads(recv)
                cmd = cmds.Commands(self, self.server)
                req = packet["req"]
                
                # validate token (on login the client doesn't have token yet)
                if req not in ["signup", "login"] and not cmd.valid_token(packet["token"]):
                    to_send = cmds.Data("err", "invalid_token").to_json()
                #exit
                elif req == "exit":
                    self.server.connections.pop(self.addr)
                    to_send = cmds.Data("suc", "exit")
                #login
                elif req == "login":
                    to_send = cmd.login(packet["data"])
                elif req == "logout":
                    to_send = cmd.log_out()
                # sign up
                elif req == "signup":
                    to_send = cmd.signup(packet["data"])
                # new game
                elif req == "new":
                    print("new game")
                    to_send = cmd.new_game(packet["data"])
                # list available games
                elif req == "aval":
                    to_send = cmd.aval_games()
                elif req == "lb":
                    print("leaderboard")
                    to_send = cmd.leaderboard()
                # req to join game
                elif req == "join":
                    to_send = cmd.join_game(packet["data"]) # to_send would be to all other client, to_self to the client who sent the request
                # ask to spec game
                elif req == "spec":
                    to_send = cmd.spec_game(packet["data"])
                elif req == "exit_game":
                    to_send = cmd.exit_game(packet["data"])
                # players makes a move
                elif req == "move":
                    to_send = cmd.move(packet["data"])
                elif req == "timer":
                    to_send = cmd.timer(packet["data"])
                elif req == "turn_ended":
                    to_send = cmd.turn_ended(packet["data"])
                elif req == "update":
                    to_send = cmd.update(packet["data"])
                
                # respond to client/s
                self.conn.send(cp.encrypt(to_send))

        except socket.timeout:
            print("Connection with {} timed out.".format(self.addr))
        except Exception as e:
            print("An error occured with {}: {}".format(self.addr, e))
        finally:
            self.server.connections.pop(self.addr)
            self.conn.close()
            print("Connection with {} closed.".format(self.addr))