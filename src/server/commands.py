import game
import json
import time
import datetime
from argon2 import PasswordHasher
import jwt
from pathlib import Path
import uuid

db_folder = Path(__file__).parents[2]
USERS_F = db_folder / "db" / "users.json"
LEADERB = db_folder / "db" /"leaderboard.json"
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
    def __init__(self, client, server):
        self.server = server
        self.client = client

    # check if the db file is free to use
    def is_data_hazard(self):
        for i in range(10):
            if not self.server.data_hazard: return False
            time.sleep(0.05)
        return True

    def generate_token(self,username):
        payload = {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithms="HS256")
    '''
    def valid_token(self,token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = payload['username']
            if username in list(map(lambda client: client.username, self.server.connections.values())): return True
        except jwt.InvalidTokenError:
            return True
    '''
    # logs in the user
    def login(self,data):
        if self.is_data_hazard(): return Data("err", "db_busy").to_json()

        self.server.data_hazard = True
        d = Data("ok", "ok")
        ph = PasswordHasher()
        username = data["username"]
        password = data["password"]

        try:
            with open(USERS_F, 'r') as f:
                db = json.load(f)
            for user in db["users"]:
                if username == user["username"]:
                    print("found user")
                    self.client.username = username
                    try:
                        #if ph.verify(user["password"],password):
                        if user["password"] == password:
                            d = Data("suc", "logged", {"username": username, "token": 1})
                        else: 
                            d = Data("err", "username or password incorrect")
                            return
                    except Exception:
                        d = Data("err", "password incorrect")
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
        ph = PasswordHasher()
        username = data["username"]
        password = data["password"]
        try:
            with open(USERS_F, "r") as f:
                db = json.load(f)
            print(db)
            for user in db["users"]:
                if user["username"] == username:
                    d = Data("err", "username taken")
                    return
            stats = {"wins": 0, "loses": 0, "draws": 0}
            print(password)
            '''try:
                hashps = ph.hash(password)
            except:
                d = Data("err", "error while signing up")
                return'''
            #print(type(hashps))
            user = {"username": username, "password": password, "stats": stats}
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
        

    def new_game(self, data, conn, username):
        print("in new game")
        g = game.Game(data["num_players"], int(uuid.uuid4()))
        self.server.games[g.id] = g
        print("created new game")
        print(self.server.games)
        #return self.join_game({"game_id": g.id}, conn, username)
        return Data("suc", "new_game", {"game_id": g.id}).to_json()
        

    def join_game(self, data, conn, username):
        g : game.Game = self.server.games[data["game_id"]]
        d = Data("ok", "ok")
        if g.max_players == len(g.players):
            d = Data("err", "full_game")
        else:
            print("adding player")
            g.add_player(conn, username)
            print(g.players)
            d = Data("suc", "joined", g.complete_game())
        return d.to_json()

    def spec_game(self, data, conn):
        g : game.Game = self.server.games[data["game_id"]]
        g.add_spectator(conn)
        return Data("suc", "spec", g.complete_game()).to_json()

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
        
    def move(self, data, username):
        g : game.Game = self.server.games[data["game_id"]]
        if g.turn is not g.usernames.index(username) : return Data("err", "not_turn").to_json()
        g.move(data["i"], data["j"])
        d = Data("suc", "move", {"player": username, "i": data["i"], "j": data["j"]})
        if g.count_moves == (g.max_players+1)**2:
            self.server.sendall = True
            d.packet["data"].pop("player")
            return d.to_json()
        elif g.check_win() : 
            self.server.sendall = True
            d.packet["msg"] = "end"
            return d.to_json()
        else:
            self.server.sendrest = True
            return d.to_json()
