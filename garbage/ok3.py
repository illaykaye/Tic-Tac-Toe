import json
import time
import datetime
from argon2 import PasswordHasher
import jwt
from pathlib import Path
import sys

db_folder = Path(__file__).parents[2]
USERS_F = db_folder / "db" / "users.json"
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


def signup(self,req):
        print(USERS_F)
        d : Data = Data("ok", "ok")
        ph = PasswordHasher()
        username = req[1]
        password = req[2]

        try:
            f = open(USERS_F, 'a')
            for line in f:
                data = json.loads(line)
                if data["username"] == username: d = Data("err", "usr_taken")
                stats = {"wins": 0, "loses": 0, "draws": 0}
                user = {"username": username, "password": ph.hash(password), "stats": stats}
                print("signing up")
                json.dump(user,f)
                f.write('\n')
                d = Data("suc", "sign_up")     
        except:
            d = Data("err", "cannot open db")
        finally:
            f.close()
            self.server.data_hazard["users"] = False
            return d.to_json()
        
if __name__=="__main__":
     req = {}