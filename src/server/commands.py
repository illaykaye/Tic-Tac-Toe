import game
import json
import time
import datetime
from argon2 import PasswordHasher
import jwt
from pathlib import Path
import sys

db_folder = Path(__file__).parents[2]
USERS_F = db_folder / "users.json"
LEADERB = db_folder / "leaderboard.json"
SECRET_KEY = "yeehaw"

class Data():
    def __init__(self, status: str, message: str, data: dict=None):
        self.packet = {
            "status": status,
            "msg": message,
            "data": data,
        }
        if data is None: self.packet.pop("data")
    
    def to_json(self):
        return json.dumps(self.packet)

class Commands():
    def __init__(self, server):
        self.server = server

    # check if the db file is free to use
    def is_data_hazard(self, file: str):
        for i in range(10):
            if not self.server.data_hazard[file]: return False
            time.sleep(0.05)
        return True

    def generate_token(self,username):
        payload = {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithms="HS256")

    def valid_token(self,token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = payload['username']
            if username in list(map(lambda client: client.username, self.server.connections.values())): return True
        except jwt.InvalidTokenError:
            return False

    # logs in the user
    def login(self,req):
        if self.is_data_hazard("users"): return Data("err", "db_busy").to_json()

        self.server.data_hazard["users"] = True

        ph = PasswordHasher()
        username = req[1]
        password = req[2]

        try:
            f = open(USERS_F, 'r')
            for line in f:
                data = json.loads(line)
                if username == data["username"]:
                    if ph.verify(data["password"],password):
                        d = Data("suc", "logged", {"username": username, "token": self.generate_token(username)})
                    else: break
            d = Data("err", "usr_pswd_incrr")
        except:
            d = Data("err", "cannot open db")
        finally:
            f.close()
            self.server.data_hazard["users"] = False
            return d.to_json()

    # signs up new user, makes sure username is unique
    def signup(self,req):
        if self.is_data_hazard("users"): return Data("err", "db_busy").to_json()

        self.server.data_hazard["users"] = True

        ph = PasswordHasher()
        username = req[1]
        password = req[2]

        try:
            f = open(USERS_F, 'a+')
            for line in f:
                data = json.loads(line)
                if data["username"] == username: d = Data("err", "usr_taken")
                stats = {"wins": 0, "loses": 0, "draws": 0}
                user = {"username": username, "password": ph.hash(password), "stats": stats}
                f.write(json.dumps(user)+'\n')
                d = Data("suc", "sign_up")     
        except:
            d = Data("err", "cannot open db")
        finally:
            f.close()
            self.server.data_hazard["users"] = False
            return d.to_json()


    def new_game(self,req,username):
        g = game.Game(req["data"]["num_players"], len(self.server.games))
        self.server.games.append(g)

        return self.join_game(self,Data("ok","insrv",{"game_id": g.id}),username)
        

    def join_game(self, req, conn, username):
        g : game.Game = self.server.games[req["data"]["game_id"]]
        if g.max_players == len(g.max_players):
            d = Data("err", "full_game")
        else:
            g.add_player(conn, username)
            d = Data("suc", "joined", {"game_id": g.id, "symbol": g.usernames.index(username)})
        return d.to_json()

    def spec_game(self, req, conn):
        g : game.Game = self.server.games[req["data"]["game_id"]]
        g.add_spectator(conn)
        return Data("suc", "specs", {"game_id": g.id}).to_json

    def aval_games(self):
        data = {}
        g : game.Game
        for g in self.server.games:
            data[g.id] = {"max_plyr": g.max_players, "num_plyr": len(g.players), "num_scep": len(g.spectators)}
        return Data("info", "aval", data).to_json()

    def leaderboard(self):
        if self.is_data_hazard("leader") : return Data("err", "db_busy").to_json()
        self.server.data_hazard["leader"] = True
        try:
            f = open(LEADERB)
            data = json.loads(f.readline())
            d = Data("info", "lb", data)
        except:
            d = Data("err", "cannot open lb")
        finally:
            self.server.data_hazard["leader"] = False
            return d.to_json()
        
    def move(self, req, username):
        g : game.Game = self.server.games[req["data"]["game_id"]]
        if g.turn is not g.usernames.index(username) : return Data("err", "not_turn").to_json()
        g.move(req["data"]["i"], req["data"]["j"])
        return 0
