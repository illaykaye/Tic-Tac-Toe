from pathlib import Path
import json
import threading

MOVE_PLAYER_LIMIT = 30
db_folder = Path(__file__).parents[2]
DB_F = db_folder / "db" / "users.json"

class Game():
    def __init__(self, x, id, server):
        self.server = server
        self.id = id
        self.grid = [[-1]*(x+1) for _ in range(x+1)]
        self.max_players = x
        self.num_players = 0
        self.players = []
        self.spectators = []
        self.current_player = 0
        self.started = False
        self.updated = {}
        self.count_moves = 0
        self.status = -2

    def add_player(self, conn, username: str):
        self.players.append((conn, username))
        self.num_players += 1
        if self.num_players == self.max_players:
            self.started = True
        self.updated[username] = False

    def add_spectator(self, conn):
        self.spectators.append(conn)

    def remove_player(self, conn, spec, username):
        if spec: self.spectators.remove(conn)
        else:
            self.players = [user for user in self.players if user[1] != username]
            self.num_players -= 1

    def updated_false(self):
        for username, _ in self.updated.items():
            self.updated[username] = False

    def move(self,i,j):
        self.count_moves += 1
        self.grid[i][j] = self.current_player
        self.status = self.check_win(i, j)
        if self.status != -2:
            self.update_users()
        self.next()

    def next(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.updated_false()

    # after a move is made check for winner
    def check_win(self, i, j):
        # Function to check if there are 3 consecutive symbols in a sequence
        def check_sequence(sequence):
            count = 0
            for symbol in sequence:
                if symbol == self.current_player:
                    count += 1
                    if count == 3:
                        return True
                else:
                    count = 0
            return False

        # Check row
        if check_sequence(self.grid[i]):
            return self.current_player
        
        # Check column
        if check_sequence([self.grid[row][j] for row in range(self.max_players+1)]):
            return self.current_player
        
        # Check diagonal (top-left to bottom-right)
        if i == j and check_sequence([self.grid[row][row] for row in range(self.max_players+1)]):
            return self.current_player
        
        # Check diagonal (top-right to bottom-left)
        if i + j == self.max_players and check_sequence([self.grid[row][self.max_players - row] for row in range(self.max_players+1)]):
            return self.current_player
        
        if self.count_moves == (self.max_players+1)**2:
            return -1
        return -2

    # check if the db file is free to use
    def is_data_hazard(self, n=0):
        if n > 10:
            return True
        if self.server.data_hazard: threading.Timer(0.5, lambda: self.is_data_hazard, n+1)
        return False

    def update_users(self):
        player_names =  [player[1] for player in self.players]
        
        try:
            # update each players num of wins, draws and loses
            with open(DB_F, "r") as f:
                f.seek(0)
                db = json.load(f)
            for user in db["users"]:
                if user["username"] in player_names:
                    if self.status == -1:
                        user["stats"]["draws"] += 1
                    elif user["username"] == player_names[self.status]:
                        user["stats"]["wins"] += 1
                    else: user["stats"]["loses"] += 1
            with open(DB_F, "w") as f:
                f.seek(0)
                json.dump(db, f, indent=4)

            # update leaderboard
            with open(DB_F, "r") as f:
                f.seek(0)
                db = json.load(f)
            lb = db["leaderboard"]
            for user in db["users"]:
                if user["username"] in player_names:
                    if user["stats"]["wins"] > lb["wins"]["num"]:
                        lb["wins"]["username"] = user["username"]
                        lb["wins"]["num"] = user["wins"]
                    if user["stats"]["draws"] > lb["draws"]["num"]:
                        lb["draws"]["username"] = user["username"]
                        lb["draws"]["username"] = user["draws"]
                    if user["stats"]["loses"] > lb["loses"]["num"]:
                        lb["loses"]["username"] = user["username"]
                        lb["loses"]["username"] = user["loses"]
            with open(DB_F, "w") as f:
                f.seek(0)
                json.dump(db, f, indent=4)
        except Exception as e:
            print("ok")
        finally:
            self.server.data_hazard = False

    def complete_game(self):
        return {
            "game_id": self.id,
            "started": self.started,
            "max_players": self.max_players,
            "num_players": self.num_players,
            "players": [player[1] for player in self.players],
            "current_player": self.current_player,
            "status": self.status,
            "grid": self.grid
        }
    

        '''
            def check_win(self,i,j):
                symbol = self.current_player - 1

                # check row
                if j == 0:
                    row_opts = [self.grid[i][0:2]]
                elif j == self.max_players:
                    row_opts = [self.grid[i][j-2:j]]
                else:
                    if self.max_players == 2:
                        row_opts = [self.grid[i][0:2]]
                    elif self.max_players == 3:
                        row_opts = [self.grid[i][k:k+2] for k in range(2)]
                    else:
                        row_opts = [self.grid[i][k:k+2] for k in range(3)]
                        if j == 1:
                            del row_opts[0]
                        elif j == 3:
                            del row_opts[2]

                for row in row_opts:
                    if all(row, symbol): 
                        return True
                
                # check column 
                if i == 0:
                    col_opts = [self.grid[0:2][j]]
                elif i == self.max_players:
                    col_opts = [self.grid[i-2:i][j]]
                else:
                    if self.max_players == 2:
                        col_opts = [self.grid[0:2][j]]
                    elif self.max_players == 3:
                        col_opts = [self.grid[k:k+2][j] for k in range(2)]
                    else:
                        col_opts = [self.grid[k:k+2][j] for k in range(3)]
                        if i == 1:
                            del col_opts[0]
                        elif i == 3:
                            del col_opts[2]

                for col in col_opts:
                    if all(col, symbol): 
                        return True

                # check diaganols
                return False'''