
class Game():
    def __init__(self, x, id):
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

    def add_player(self, conn, username: str):
        self.players.append((conn, username))
        self.num_players += 1
        if self.num_players == self.max_players:
            self.started = True
        self.updated[username] = False

    def add_spectator(self, conn):
        self.spectators.append(conn)

    def remove_player(self, conn, spec, username=None):
        if spec: self.spectators.remove(conn)
        else:
            self.players = list(filter(lambda tup: tup[1] != username, self.players))

    def updated_false(self):
        for username, _ in self.updated.items():
            self.updated[username] = False

    def move(self,i,j):
        self.grid[i,j] = self.current_player
        self.count_moves += 1
        self.current_player = (self.current_player + 1) % len(self.players)
        
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
        return False
    def all_clients(self):
        return [player[0] for player in self.players] + self.spectators
    def complete_game(self):
        return {
            "game_id": self.id,
            "started": self.started,
            "max_players": self.max_players,
            "num_players": self.num_players,
            "players": [player[1] for player in self.players],
            "current_player": self.current_player,
            "grid": self.grid
        }
    def end(self, res):
        if res == -1:
            return "draw"
        else:
            return self.usernames[res]