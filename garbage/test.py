import tkinter as tk
import threading
import time

class MyTimer(threading.Timer):
    def __init__(self, interval, function, *args, **kwargs):
        self._remaining_time = interval
        super().__init__(interval, function, *args, **kwargs)
        self._start_time = time.time()

    def remaining_time(self):
        return self._remaining_time - (time.time() - self._start_time)

class TicTacToeGame(tk.Tk):
    def __init__(self, n_players, n=4):
        super().__init__()
        self.symbols = ['x','○','△','□']
        self.title("Tic Tac Toe")
        self.n = n
        self.n_players = n_players
        self.current_player = 0
        self.player_names = [f"Player {i+1}" for i in range(n_players)]
        self.timer = MyTimer(30, lambda: self.switch_player())
        self.update_timer = MyTimer(1, lambda: self.update_time())
        self.timer_labels = []

        self.create_widgets()

    def create_widgets(self):
        # Tic Tac Toe grid
        self.tic_tac_toe_grid = [[None for _ in range(self.n)] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                self.tic_tac_toe_grid[i][j] = tk.Button(self, text=" ", font=('Arial', 20), command=lambda i=i,j=j: self.move(i,j), width=5, height=2)
                self.tic_tac_toe_grid[i][j].grid(row=i, column=j) 

        # Player list
        self.player_labels = []
        for i in range(self.n_players):
            player_name = tk.Label(self, text=self.player_names[i])
            if i == 0: player_name.config(font=('Arial', 12, 'bold'))
            player_name.grid(row=i, column=self.n+1)
            self.player_labels.append(player_name)

        # Timer
        self.timer_label = tk.Label(self, text="00:00", font=('Arial', 12))
        self.timer_label.grid(row=self.n_players+1, column=self.n+1)

    def move(self, i, j):
        self.tic_tac_toe_grid[i][j].config(text=self.symbols[self.current_player],state=tk.DISABLED)
        self.switch_player()
    
    def update_time(self):
        remaining_time = self.timer.remaining_time()
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=time_str)

        if remaining_time >= 0:
            self.update_timer = MyTimer(1, lambda: self.update_time())
            self.update_timer.start()
        else:
            print("hello")

    def switch_player(self):
        self.timer.cancel()
        self.update_timer.cancel()
        self.timer = MyTimer(30, lambda: self.switch_player())
        self.update_timer = MyTimer(1, lambda: self.update_time())
        self.timer.start()
        self.update_timer.start()
        self.current_player = (self.current_player + 1) % self.n_players
        # Highlight current player's name
        for i, label in enumerate(self.player_labels):
            if i == self.current_player:
                label.config(font=('Arial', 12, 'bold'))
            else:
                label.config(font=('Arial', 12))

    def run_game(self):
        self.timer.start()  # Set the time limit for each player's turn
        self.update_timer.start()
if __name__ == "__main__":
    n_players = 2  # Change this to the desired number of players
    game = TicTacToeGame(n_players, 3)
    game.run_game()
    game.mainloop()

