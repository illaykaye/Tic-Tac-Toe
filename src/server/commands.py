import game
import json
import time
import src.server.server as srv
from argon2 import PasswordHasher

USERS_F = "users.json"
class Data():
    def __init__(self, status: str, message: str, data: dict=None):
        self.packet = {
            "status": status,
            "msg": message,
            "data": data,
            "timestamp": time.time()
        }
        if data is None: self.packet.pop("data")
    
    def to_json(self):
        return json.dumps(self.packet)

class Commands():
    def __init__(self, server: srv.Server):
        self.server = server

    # check if the db file is free to use
    def is_data_hazard(self):
        for i in range(10):
            if not self.server.data_hazard: return False
            time.sleep(0.05)
        return True

    # logs in the user
    def login(self,req):
        if self.is_data_hazard: return Data("err", "db_busy").to_json()

        self.server.data_hazard = True

        ph = PasswordHasher()
        username = req[1]
        password = req[2]

        try:
            f = open(USERS_F, 'r')
            for line in f:
                data = json.loads(line)
                if username == data["username"]:
                    if ph.verify(data["password"],password):
                        d = Data("suc", "logged", {"username": username})
                    else: break
            d = Data("err", "usr_pswd_incrr")
        except:
            d = Data("err", "cannot open db")
        finally:
            f.close()
            self.server.data_hazard = False
            return d.to_json()

    # signs up new user, makes sure username is unique
    def signup(self,req):
        if self.is_data_hazard: return Data("err", "db_busy").to_json()

        self.server.data_hazard = True

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
            self.server.data_hazard = False
            return d.to_json()


    def new_game(self,req):
        x = req[1]
        

    def join_game(conn, g: game.Game):
        if g.max_players == len(g.max_players):
            return "full"
        else:
            g.add_player(conn)
            return "cnctd"

    def spec_game(self, req):
        return 0

    def aval_games(games: list[game.Game]):
        data = {}
        for g in games:
            data[g.id] = {"max_plyr": g.max_players, "num_plyr": len(g.players), "num_scep": len(g.spectators)}

    def leaderboard():
        return 1
    
    def move(self, req):
        return 0
