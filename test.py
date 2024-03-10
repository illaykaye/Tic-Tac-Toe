import tkinter as tk
import time

class TicTacToeGame(tk.Tk):
    def __init__(self, n_players, n=4):
        super().__init__()

        self.title("Tic Tac Toe")
        self.n = n
        self.n_players = n_players
        self.current_player = 0
        self.player_names = [f"Player {i+1}" for i in range(n_players)]

        self.timer_labels = []

        self.create_widgets()

    def create_widgets(self):
        # Tic Tac Toe grid
        self.tic_tac_toe_grid = [[None for _ in range(self.n)] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                self.tic_tac_toe_grid[i][j] = tk.Button(self, text=" ", font=('Arial', 20), width=5, height=2)
                self.tic_tac_toe_grid[i][j].grid(row=i, column=j)

        # Player list
        self.player_labels = []
        for i in range(self.n_players):
            player_name = tk.Label(self, text=self.player_names[i])
            player_name.grid(row=i, column=self.n+1)
            self.player_labels.append(player_name)

        # Timer
        self.timer_label = tk.Label(self, text="00:00", font=('Arial', 12))
        self.timer_label.grid(row=self.n_players+1, column=self.n+1)

    def start_timer(self, time_limit):
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            remaining_time = max(time_limit - elapsed_time, 0)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            time_str = f"{minutes:02}:{seconds:02}"
            self.timer_label.config(text=time_str)
            self.update()
            if remaining_time <= 0:
                break

    def switch_player(self):
        self.current_player = (self.current_player + 1) % self.n_players
        # Highlight current player's name
        for i, label in enumerate(self.player_labels):
            if i == self.current_player:
                label.config(font=('Arial', 12, 'bold'))
            else:
                label.config(font=('Arial', 12))

    def run_game(self):
        while True:
            self.switch_player()
            self.start_timer(30)  # Set the time limit for each player's turn

if __name__ == "__main__":
    n_players = 3  # Change this to the desired number of players
    game = TicTacToeGame(n_players)
    game.run_game()
    game.mainloop()

