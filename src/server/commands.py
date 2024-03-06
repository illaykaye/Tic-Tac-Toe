import game
import json
from argon2 import PasswordHasher

USERS_F = "users.json"

def login(req):
    ph = PasswordHasher()
    username = req[1]
    password = req[2]
    with open(USERS_F) as f:
        for line in f:
            data = json.loads(line)
            if username == data["username"]:
                if ph.verify(data["password"],password):
                    return True
        return False

def signup(req):
    username = req[1]
    password = req[2]
    with open(USERS_F) as f:
        for line in f:
            data = json.loads(line)
            if data["username"] == username: return 0
            ph = PasswordHasher()
            stats = {"wins": 0, "loses": 0, "draws": 0}
            user = {"username": username, "password": ph.hash(password), "stats": stats}
            f.write(json.dumps(user)+'\n')
            return 1

def new_game(req,id):
    x = req[1]
    return game.Game(x,id)

def join_game(conn, g: game.Game):
    if g.max_players == len(g.max_players):
        return "full"
    else:
        g.add_player(conn)
        return "cnctd"

def aval_games(games: list[game.Game]):
    data = {}
    for g in games:
        data[g.id] = {"max_plyr": g.max_players, "num_plyr": len(g.players), "num_scep": len(g.spectators)}

def leaderboard():
    return 1
