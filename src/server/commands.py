import game
import json
import time
import threading
import hashlib
import jwt
from pathlib import Path
import uuid

db_folder = Path(__file__).parents[2]
DB_F = db_folder / "db" / "users.json"
SECRET_KEY = "yeehaw"

FORMAT = 'utf-8'

# defines the format in which messages will be sent from the server to the client
class Data():
    def __init__(self, status: str, message: str, data: dict=None):
        self.packet = {
            "status": status,
            "msg": message,
            "data": data,
        }
        if data is None: self.packet.pop("data")
    
    def to_json(self):
        return json.dumps(self.packet) # converts the dict to JSON format

# defines all necessary commands the server needs to perform
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
    
    # makes sure the token sent with each of the client's packets is valid
    def valid_token(self,token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = payload['username']
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
            with open(DB_F, 'r') as f:
                db = json.load(f)
            if len(db["users"]) == 0:
                d = Data("err", "no such user exists")
                return
            for user in db["users"]:
                if username == user["username"]: # searching for a user with the username given by the client
                    password_bytes = password.encode(FORMAT)
                    hasher = hashlib.sha256()
                    hasher.update(password_bytes)
                    hashed_password = hasher.hexdigest()
                    if user["password"] == hashed_password: # check if the passwords match
                        self.client.username = username
                        d = Data("suc", "logged", {"username": username, "token": self.generate_token(username)})
                        break
                d = Data("err", "username or password incorrect")
        except:
            d = Data("err", "cannot open db")
        finally:
            self.server.data_hazard = False # frees the db
            return d.to_json()

    # signs up new user, makes sure username is unique
    def signup(self,data):
        if self.is_data_hazard(): return Data("err", "db_busy").to_json()
        self.server.data_hazard = True
        d : Data = Data("ok", "ok")
        username = data["username"]
        password: str = data["password"]

        password_bytes = password.encode(FORMAT)
        hasher = hashlib.sha256()
        hasher.update(password_bytes)
        hashed_password = hasher.hexdigest() # hash the password to save

        try:
            with open(DB_F, "r") as f:
                db = json.load(f)
            for user in db["users"]:
                if user["username"] == username:
                    d = Data("err", "username taken")
                    return
            stats = {"wins": 0, "loses": 0, "draws": 0} # initialize user stats to 0
            user = {"username": username, "password": hashed_password, "stats": stats}
            db["users"].append(user) # adding new user to the db
            with open(DB_F, "w") as f:
                f.seek(0)
                json.dump(db, f, indent=4) # writing back the db
                d = Data("suc", "signup", {"username": username})
        except Exception as e:
            d = Data("err", e)
        finally:
            self.server.data_hazard = False # frees the db
            return d.to_json()

    # reuturns a list of all available games
    def aval_games(self):
        data = {}
        g : game.Game
        for g in self.server.games.values(): # creating a list of all ongoing games
            data[g.id] = {"max_players": g.max_players, "num_players": len(g.players), "num_spec": len(g.spectators)}
        return Data("info", "aval", data).to_json()

    # returns the leaderboard of all games ever played
    def leaderboard(self):
        if self.is_data_hazard() : return Data("err", "db_busy").to_json()
        self.server.data_hazard = True
        d = Data("ok", "ok")
        try:
            with open(DB_F, "r") as f:
                db = json.load(f)
            d = Data("info", "lb", db["leaderboard"]) # returning the leaderboard stats
        except:
            d = Data("err", "cannot open db")
        finally:
            self.server.data_hazard = False
            return d.to_json()        

    # creates a new game and joins the client that created the game to it
    def new_game(self, data):
        g = game.Game(data["num_players"], int(uuid.uuid4()), self.server)
        self.server.games[g.id] = g
        return self.join_game({"game_id": g.id})
        
    # logs the client out of the user 
    def log_out(self):
        self.client.username = ''
        return Data("suc", "logout").to_json()

    # joins the client to a game based on the ID the server got from the client
    def join_game(self, data):
        g : game.Game = self.server.games.get(data["game_id"])
        if g is None:
            return Data("err", "game doesn't exist").to_json()
        if g.max_players == len(g.players):
            return Data("err", "full_game").to_json()
        else:
            self.client.in_game = True
            g.add_player(self.client.conn, self.client.username)
            g.updated_false()
            return Data("game", "joined", g.complete_game()).to_json()
    
    # provides the user with the info needed to spectate the game, adds him to the spectators list
    def spec_game(self, data):
        g : game.Game = self.server.games.get(data["game_id"])
        if g is None: return Data("err", "game doesn't exist").to_json()
        g.add_spectator(self.client.username)
        return Data("game", "spec", g.complete_game()).to_json()

    # based on whether the client is a spectator or a player the function removes the client from the game
    def exit_game(self, data):
        print("exiting game")
        g : game.Game = self.server.games.get(data["game_id"])
        if g is None: return Data("err", "game doesn't exist").to_json()
        g.remove_player(self.client.username, data["spec"])
        self.client.in_game = False
        if g.num_players == 0 and len(g.spectators) == 0:
            del self.server.games[g.id]
        if data["destroy"]:
            return Data("suc", "exit").to_json()
        else:
            return Data("game", "user_left_game", {"username": self.client.username}).to_json()
    
    # returns the complete data needed to display the game on each client' GUI
    # is called per request of each client to be updated
    def update(self, data):
        g : game.Game = self.server.games.get(data["game_id"])
        if g is None: return Data("err", "game doesn't exist").to_json()
        if not g.updated[self.client.username]:
            g.updated[self.client.username] = True
            return Data("game", "update", g.complete_game()).to_json()
        else:
            return Data("game", "no_update").to_json()

    # skips a player after he inform the player he had not made a move within the time limit
    # the client side automatically informs the server the player had not made a move
    def turn_ended(self, data):
        g : game.Game = self.server.games.get(data["game_id"])
        if g is None: return Data("err", "game doesn't exist").to_json()
        g.next()
        #g.timesup[self.client.username] = True
        return Data("game", "turn_ended").to_json()

    # makes a move on the board
    def move(self, data):
        g : game.Game = self.server.games.get(data["game_id"])
        if g is None: return Data("err", "game doesn't exist").to_json()
        if g.players[g.current_player][1] != self.client.username: return Data("err", "not_turn").to_json() # checks if its his turn
        g.move(data["i"], data["j"])
        return Data("game", "move", {"player": self.client.username, "i": data["i"], "j": data["j"]}).to_json()
        