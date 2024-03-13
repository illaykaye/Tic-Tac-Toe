import game
import json
import time
import threading
import hashlib
import jwt
from pathlib import Path
import uuid

db_folder = Path(__file__).parents[2]
USERS_F = db_folder / "db" / "users.json"
LEADERB = db_folder / "db" /"leaderboard.json"
SECRET_KEY = "yeehaw"

FORMAT = 'utf-8'

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
    def __init__(self, client, server):
        self.server = server
        self.client = client

    # check if the db file is free to use
    def is_data_hazard(self, n=0):
        if n > 10:
            return True
        if self.server.data_hazard: threading.Timer(0.5, lambda: self.is_data_hazard, n+1)
        return False

    def generate_token(self,username):
        encoded_jwt = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    def valid_token(self,token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print(payload)
            username = payload['username']
            print(username)
            for _, client in self.server.connections.items():
                if username == client.username:
                    return True
        except jwt.InvalidTokenError:
            return False
    
    # logs in the user
    def login(self,data):
        if self.is_data_hazard(): return Data("err", "db_busy").to_json()

        self.server.data_hazard = True
        d = Data("ok", "ok")

        username = data["username"]
        password: str = data["password"]
        
        for _, client in self.server.connections.items():
                if username == client.username:
                    return Data("err", "user already logged in").to_json()

        try:
            with open(USERS_F, 'r') as f:
                db = json.load(f)
            if len(db["users"]) == 0:
                d = Data("err", "no such user exists")
                return
            for user in db["users"]:
                if username == user["username"]:
                    print("found user")
                    self.client.username = username
                    password_bytes = password.encode(FORMAT)
                    hasher = hashlib.sha256()
                    hasher.update(password_bytes)
                    hashed_password = hasher.hexdigest()
                    if user["password"] == hashed_password:
                        print("user correct")
                        d = Data("suc", "logged", {"username": username, "token": self.generate_token(username)})
                    else: 
                        d = Data("err", "username or password incorrect")
                        return
        except:
            d = Data("err", "cannot open db")
        finally:
            self.server.data_hazard = False
            return d.to_json()

    # signs up new user, makes sure username is unique
    def signup(self,data):
        if self.is_data_hazard(): return Data("err", "db_busy").to_json()
        print(USERS_F)
        self.server.data_hazard = True
        d : Data = Data("ok", "ok")
        username = data["username"]
        password: str = data["password"]

        password_bytes = password.encode(FORMAT)
        hasher = hashlib.sha256()
        hasher.update(password_bytes)
        hashed_password = hasher.hexdigest()

        try:
            with open(USERS_F, "r") as f:
                db = json.load(f)
            print(db)
            for user in db["users"]:
                if user["username"] == username:
                    d = Data("err", "username taken")
                    return
            stats = {"wins": 0, "loses": 0, "draws": 0}
            user = {"username": username, "password": hashed_password, "stats": stats}
            db["users"].append(user)
            with open(USERS_F, "w") as f:
                f.seek(0)
                json.dump(db, f, indent=4)
                d = Data("suc", "signup", {"username": username})
        except Exception as e:
            d = Data("err", e)
        finally:
            self.server.data_hazard = False
            return d.to_json()

    def aval_games(self):
        data = {}
        g : game.Game
        for g in self.server.games.values():
            data[g.id] = {"max_players": g.max_players, "num_players": len(g.players), "num_spec": len(g.spectators)}
        return Data("info", "aval", data).to_json()

    def leaderboard(self):
        if self.is_data_hazard() : return Data("err", "db_busy").to_json()
        self.server.data_hazard = True
        d = Data("ok", "ok")
        try:
            with open(USERS_F, "r") as f:
                db = json.load(f)
            d = Data("info", "lb", db["leaderboard"])
        except:
            d = Data("err", "cannot open db")
        finally:
            self.server.data_hazard = False
            return d.to_json()        

    def new_game(self, data):
        print("in new game")
        g = game.Game(data["num_players"], int(uuid.uuid4()))
        self.server.games[g.id] = g
        print("created new game")
        print(self.server.games)
        return self.join_game({"game_id": g.id})
        #return Data("suc", "new_game", {"game_id": g.id}).to_json()
        
    def log_out(self):
        self.client.username = ''
        return Data("suc", "logout").to_json()

    def join_game(self, data):
        g : game.Game = self.server.games[data["game_id"]]
        if g.max_players == len(g.players):
            return Data("err", "full_game").to_json()
        else:
            g.add_player(self.client.conn, self.client.username)
            g.updated_false()
            return Data("game", "joined", g.complete_game()).to_json()
        
    def spec_game(self, data):
        g : game.Game = self.server.games[data["game_id"]]
        g.add_spectator(self.client.conn)
        return Data("game", "spec", g.complete_game()).to_json()

    def exit_game(self, data):
        g : game.Game = self.server.games[data["game_id"]]
        g.remove_player(data["spec"], self.client.conn, self.client.username)
        if data["spec"]:
            return (Data("suc", "left_spec").to_json(), None)
        else:
            return Data("game", "user_left_game", {"username": self.client.username}).to_json()
    
    def update(self, data):
        g : game.Game = self.server.games[data["game_id"]]
        if not g.updated[self.client.username]:
            g.updated[self.client.username] = True
            return Data("game", "update", g.complete_game()).to_json()
        else:
            return Data("game", "no_update").to_json()

    def turn_ended(self, data):
        g : game.Game = self.server.games[data["game_id"]]
        g.next()
        #g.timesup[self.client.username] = True
        return Data("game", "turn_ended").to_json()


    def move(self, data):
        g : game.Game = self.server.games[data["game_id"]]
        if g.players[g.current_player][1] != self.client.username: return Data("err", "not_turn").to_json()
        g.move(data["i"], data["j"])
        #g.check_win()
        return Data("game", "move", {"player": self.client.username, "i": data["i"], "j": data["j"]}).to_json()
        