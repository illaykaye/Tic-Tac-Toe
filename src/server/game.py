from pathlib import Path
import json
import threading

db_folder = Path(__file__).parents[2]
DB_F = db_folder / "db" / "users.json"

class Game():
    def __init__(self, x, id, server):
        self.server = server
        self.id = id
        self.grid = [[-1]*(x+1) for _ in range(x+1)]
        self.max_players = x
        self.num_players = 0
        self.spectators = []
        self.players = []
        self.left_players = [] # players that left the game mid-game
        self.current_player = 0
        self.started = False
        self.updated = {} # dict that has clients as keys and a boolean 
        #indicating whether that have been updated since last change or not
        self.count_moves = 0 # num of moves made so far
        self.status = -2

    # adding a player to the game | if reached max players, the game starts
    def add_player(self, conn, username: str):
        self.players.append((conn, username))
        self.num_players += 1
        if self.num_players == self.max_players:
            self.started = True
        self.updated[username] = False

    def add_spectator(self, username: str):
        self.spectators.append(username)
        self.updated[username] = False

    # removing a player = adding him the the list of players that left
    # this way the game knows to skip on him
    # if game hasn't started yet, we jut remove him completely from the players list
    # if it has started we want to still see him on the list, this way we make sure no one else will use his symbol
    def remove_player(self, username, spec):
        if spec:
            self.spectators.remove(username)
        elif self.started and self.status == -2:
            self.left_players.append(username)
        else:
            self.players = [user for user in self.players if user[1] != username]
            self.num_players -= 1

    # after a move is made, or someone joins the game
    def updated_false(self):
        for username, _ in self.updated.items():
            self.updated[username] = False

    # make a move on the board
    # checks if this move made the current player win
    def move(self,i,j):
        self.count_moves += 1
        self.grid[i][j] = self.current_player
        self.status = self.check_win(i, j)
        if self.status != -2:
            self.update_users()
        self.next()

    def next(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        if self.players[self.current_player][1] in self.left_players: self.next()
        self.updated_false()

    # for each coordinate in which a player place a symbol
    # there are 12 combinations of tuples (i,j) of coordinates (in each direction, the last move can be the first, middle or last)
    # that can be a possible winning row, column or diagonal
    # that include that last move made by the player
    # this function returns all combinations that are within the bounds of the grid 
    def win_cases(self, i, j):
        cases = []
        discard_case = False
        # rows
        for k in range(3):
            case = []
            if j-k < 0: break
            for n in range(3):
                if j-k+n < self.max_players+1:
                    case.append(self.grid[i][j-k+n])
                else: 
                    discard_case = True
            if not discard_case: cases.append(case)
            discard_case = False

        # columns
        for k in range(3):
            case = []
            if i-k < 0: break
            for n in range(3):
                if i-k+n < self.max_players+1:
                    case.append(self.grid[i-k+n][j])
                else:
                    discard_case = True
            if not discard_case: cases.append(case)
            discard_case = False

        # diagonals (ex: i=0,j=0: [(0,0), (1,1), (2,2)])
        for k in range(3):
            case = []
            if i-k < 0 or j-k < 0: break
            for n in range(3):
                if i-k+n < self.max_players+1 and j-k+n < self.max_players+1:
                    case.append(self.grid[i-k+n][j-k+n])
                else:
                    discard_case = True
            if not discard_case: cases.append(case)
            discard_case = False

        # opposite diagonals (ex: i=2,j=0: [(2,0), (1,1), (0,2)])
        for k in range(3):
            case = []
            if i+k > self.max_players or j-k < 0: break
            for n in range(3):
                if i+k-n < 0 and j-k+n < self.max_players+1:
                    case.append(self.grid[i+k-n][j-k+n])
                else:
                    discard_case = True
            if not discard_case: cases.append(case)
            discard_case = False
        return cases

    # after a move is made check for winner
    def check_win(self, i, j):
        cases = self.win_cases(i,j)
        for case in cases:
            if all(sym == self.current_player for sym in case):
                return self.current_player # current player (the one who made the move) wins
        if self.count_moves == (self.max_players+1)**2:
            return -1 # draw
        return -2 # no win or draw, game continues

    # check if the db file is free to use
    def is_data_hazard(self, n=0):
        if n > 10:
            return True
        if self.server.data_hazard: threading.Timer(0.5, lambda: self.is_data_hazard, n+1)
        return False

    # after a win was made, this functions updates their stats
    def update_users(self):
        player_names =  [player[1] for player in self.players]
        
        try:
            # update each players num of wins, draws and loses
            with open(DB_F, "r") as f:
                f.seek(0)
                db = json.load(f)
            print(db)
            for user in db["users"]:
                print(user["stats"])
                if user["username"] in player_names:
                    if self.status == -1:
                        user["stats"]["draws"] += 1
                    elif user["username"] == player_names[self.status]:
                        user["stats"]["wins"] += 1
                    else: user["stats"]["loses"] += 1            
            
            lb = db["leaderboard"]
            for user in db["users"]: # updating the leaderboard
                if user["username"] in player_names:
                    if user["stats"]["wins"] > lb["wins"]["num"]:
                        lb["wins"]["username"] = user["username"]
                        lb["wins"]["num"] = user["stats"]["wins"]
                    if user["stats"]["draws"] > lb["draws"]["num"]:
                        lb["draws"]["username"] = user["username"]
                        lb["draws"]["num"] = user["stats"]["draws"]
                    if user["stats"]["loses"] > lb["loses"]["num"]:
                        lb["loses"]["username"] = user["username"]
                        lb["loses"]["num"] = user["stats"]["loses"]
            with open(DB_F, "w") as f:
                f.seek(0)
                json.dump(db, f, indent=4)
        finally:
            self.server.data_hazard = False

    # returns the complete data needed for each client to display the game
    def complete_game(self):
        return {
            "game_id": self.id,
            "started": self.started,
            "max_players": self.max_players,
            "num_players": self.num_players,
            "players": [player[1] for player in self.players],
            "left_players": self.left_players,
            "current_player": self.current_player,
            "status": self.status,
            "grid": self.grid
        }
    