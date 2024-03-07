
class Game():
    def __init__(self, x, id):
        self.id = id
        self.board = [[0]*x for _ in range(x)]
        self.max_players = x
        self.players = {}
        self.usernames = []
        self.spectators = []
        self.turn = 0
        self.count_moves = 0

    def add_player(self, player, username: str):
        self.usernames.append(username)
        self.players[username] = player

    def add_spectator(self, spec):
        self.spectators.append(spec)

    def move(self,i,j):
        self.board[i,j] = self.turn
        self.count_moves += 1
        self.turn = (self.turn + 1) % len(self.players)

        if self.count_moves == (self.max_players+1)**2: return self.end(-1)
        elif self.check_win : return self.end(self.turn-1)
        
    def check_win(self,i,j):
        symbol = self.turn - 1

        # check row
        if j == 0:
            row_opts = [self.board[i][0:2]]
        elif j == self.max_players:
            row_opts = [self.board[i][j-2:j]]
        else:
            if self.max_players == 2:
                row_opts = [self.board[i][0:2]]
            elif self.max_players == 3:
                row_opts = [self.board[i][k:k+2] for k in range(2)]
            else:
                row_opts = [self.board[i][k:k+2] for k in range(3)]
                if j == 1:
                    del row_opts[0]
                elif j == 3:
                    del row_opts[2]

        for row in row_opts:
            if all(row, symbol): 
                return True
        
        # check column 
        if i == 0:
            col_opts = [self.board[0:2][j]]
        elif i == self.max_players:
            col_opts = [self.board[i-2:i][j]]
        else:
            if self.max_players == 2:
                col_opts = [self.board[0:2][j]]
            elif self.max_players == 3:
                col_opts = [self.board[k:k+2][j] for k in range(2)]
            else:
                col_opts = [self.board[k:k+2][j] for k in range(3)]
                if i == 1:
                    del col_opts[0]
                elif i == 3:
                    del col_opts[2]

        for col in col_opts:
            if all(col, symbol): 
                return True

        # check diaganols
        return False
    
    def end(self, res):
        if res == -1:
            return "draw"
        else:
            return self.usernames[res]