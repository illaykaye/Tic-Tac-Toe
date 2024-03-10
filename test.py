import tkinter as tk

def join_game(game_id):
    # Function to join the selected game
    game = games.get(game_id)
    if game['num_players'] < game['max_players']:
        game['num_players'] += 1
        print(f"Joined game {game_id}")
    else:
        print(f"Game {game_id} is already full!")

def display_games(games):
    # Function to display all games in a Tkinter window
    root = tk.Tk()
    root.title("Available Games")

    for game_id, game_props in games.items():
        label_text = f"Game {game_id}: {game_props['num_players']}/{game_props['max_players']} players"
        if game_props['num_players'] < game_props['max_players']:
            button_text = "Join"
            command = lambda id=game_id: join_game(id)
        else:
            button_text = "Full"
            command = None

        frame = tk.Frame(root)
        frame.pack()

        label = tk.Label(frame, text=label_text)
        label.grid(row=0, column=0, padx=5, pady=5)

        button = tk.Button(frame, text=button_text, command=command)
        button.grid(row=0, column=1, padx=5, pady=5)

    root.mainloop()

# Example usage:
games = {
    1: {'max_players': 4, 'num_players': 2, 'num_spectators': 0},
    2: {'max_players': 2, 'num_players': 1, 'num_spectators': 0},
    3: {'max_players': 6, 'num_players': 6, 'num_spectators': 2}
}

display_games(games)