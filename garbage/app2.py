import tkinter as tk
import tkinter.ttk as ttk
import clnt

class App(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.title("Tic Tac Toe")
        self.geometry('300x350')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.clnt = clnt.Client(self.handle_response)
        self.clnt.start_client()

        self.current_frame = None
        self.show_frame(StartPage)

    def handle_response(self, res):
        if res["status"] == "err":
            self.show_error(res["msg"])
        elif res["status"] == "suc":
            if res["msg"] == "connected":
                self.show_frame(StartPage)
            elif res["msg"] == "logged":
                self.clnt.token = res["data"]["token"]
                self.clnt.username = res["data"]["username"]
                self.show_frame(MainPage)
            elif res["msg"] == "signup":
                self.show_frame(StartPage)
            elif res["msg"] in ["joined", "spec"]:
                self.clnt.game_id = res["data"]["game_id"]
                self.show_frame(TicTacToeGame, res)
            elif res["msg"] == "user_left_game":
                self.show_frame(MainPage)
        elif res["status"] == "info":
            if res["msg"] == "aval":
                self.show_frame(AvailableGamesPage, res["data"])
            elif res["msg"] == "lb":
                self.show_frame(LeaderPage, res["data"])

    def show_frame(self, frame_class, data=None):
        new_frame = frame_class(self)
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = new_frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_error(self, err):
        error_win = tk.Toplevel(self)
        error_win.title("Error")
        error_win.geometry('300x60')
        ttk.Label(error_win, text=err, font=("ubuntu", 14), foreground='red').pack()

    def on_closing(self):
        self.clnt.request("exit")
        self.destroy()

class StartPage(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        ttk.Label(self, text="Tic Tac Toe", font=("ubuntu", 16)).pack(pady=2, expand=True)
        ttk.Button(self, text="Login", command=self.login_page).pack(pady=3, expand=True)
        ttk.Button(self, text="Signup", command=self.signup_page).pack(pady=1)
        ttk.Button(self, text='Exit', command=self.parent.on_closing).pack(pady=3, expand=True)

        self.pack(fill=tk.BOTH, expand=True)

    def login_page(self):
        self.parent.show_frame(LoginPage)

    def signup_page(self):
        self.parent.show_frame(SignupPage)

class LoginPage(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        username = tk.StringVar()
        password = tk.StringVar()

        ttk.Label(self, text="Username:", font=("ubuntu, 12")).grid(row=0, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=username).grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(self, text="Password:", font=("ubuntu, 12")).grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=password, show="*").grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(self, text="Back", command=lambda: self.parent.show_frame(StartPage)).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(self, text="Login", command=lambda: self.parent.clnt.request("login", username.get(), password.get())).grid(row=2, column=1, padx=10, pady=10)

        self.pack(fill=tk.BOTH, expand=True)

class SignupPage(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        username = tk.StringVar()
        password = tk.StringVar()

        ttk.Label(self, text="Username:", font=("ubuntu, 12")).grid(row=0, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=username).grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(self, text="Password:", font=("ubuntu, 12")).grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=password, show="*").grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(self, text="Back", command=lambda: self.parent.show_frame(StartPage)).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(self, text="Signup", command=lambda: self.parent.clnt.request("signup", username.get(), password.get())).grid(row=2, column=1, padx=10, pady=10)

        self.pack(fill=tk.BOTH, expand=True)

class MainPage(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        ttk.Label(self, text="Welcome {}!".format(self.parent.clnt.username), font=("ubuntu", 16)).pack(pady=2, expand=True)
        ttk.Button(self, text="New Game", command=self.parent.show_new_game_page).pack(pady=3, expand=True)
        ttk.Button(self, text="Available Games", command=lambda: self.parent.clnt.request("aval")).pack(pady=1)
        ttk.Button(self, text="Leaderboard", command=lambda: self.parent.clnt.request("lb")).pack(pady=1, expand=True)
        ttk.Button(self, text='Exit', command=self.parent.on_closing).pack(pady=3, expand=True)

        self.pack(fill=tk.BOTH, expand=True)

class LeaderPage(ttk.Frame):

    def __init__(self, parent, data):
        super().__init__(parent)
        self.parent = parent

        ttk.Label(self, text="Leaderboard", font=("ubuntu", 16)).pack(pady=3, expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["wins"]["username"], data["wins"]["num"])).pack(pady=3, expand=True)
        ttk.Label(self, text="Most loses: {}, {}".format(data["loses"]["username"], data["loses"]["num"])).pack(pady=3, expand=True)
        ttk.Label(self, text="Most draws: {}, {}".format(data["draws"]["username"], data["draws"]["num"])).pack(pady=3, expand=True)
        ttk.Button(self, text="Back", command=lambda: self.parent.show_frame(MainPage)).pack(pady=3, expand=True)

        self.pack(fill=tk.BOTH, expand=True)

class NewGamePage(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        ttk.Label(self, text="Choose number of players:", font=("ubuntu", 14)).pack(pady=2, expand=True)
        ttk.Button(self, text="2", command=lambda: self.parent.clnt.request("new", 2)).pack(pady=3, expand=True)
        ttk.Button(self, text="3", command=lambda: self.parent.clnt.request("new", 3)).pack(pady=1)
        ttk.Button(self, text="4", command=lambda: self.parent.clnt.request("new", 4)).pack(pady=1, expand=True)
        ttk.Button(self, text="Back", command=lambda: self.parent.show_frame(MainPage)).pack(pady=3, expand=True)

        self.pack(fill=tk.BOTH, expand=True)

class AvailableGamesPage(ttk.Frame):

    def __init__(self, parent, data):
        super().__init__(parent)
        self.parent = parent

        ttk.Label(self, text="Available Games", font=("ubuntu", 16)).pack(pady=3, expand=True)

        if len(data) == 0:
            ttk.Label(self, text="No games available").pack(pady=3, expand=True)
        else:
            for game_id, game in data.items():
                game_info = f"Game: {game_id}, Max Players: {game['max_players']}, Players in Game: {game['num_players']}, Spectators: {game['num_spec']}"

                if game["num_players"] < game["max_players"]:
                    button_text = "Join"
                    state = tk.NORMAL
                    command = lambda id=game_id: self.parent.clnt.request("join", id)
                else:
                    button_text = "Full"
                    command = None
                    state = tk.DISABLED

                ttk.Label(self, text=game_info).pack(pady=5, expand=True)
                ttk.Button(self, text=button_text, command=command, state=state).pack(pady=1, expand=True)
                ttk.Button(self, text="Spectate", command=lambda id=game_id: self.parent.clnt.request("spec", id)).pack(pady=1, expand=True)

                ttk.Frame(self, height=1, background="gray").pack(fill=tk.X, padx=5, pady=2)  # Separator between game entries

        ttk.Button(self, text="Back", command=lambda: self.parent.show_frame(MainPage)).pack(pady=5, expand=True)

        self.pack(fill=tk.BOTH, expand=True)

class TicTacToeGame(tk.Toplevel):

    def __init__(self, parent, res):
        super().__init__(parent)
        self.parent = parent
        self.symbols = ['x', '○', '△', '□']
        self.max_players = res["data"]["max_players"]
        self.num_players = res["data"]["num_players"]
        self.board = res["data"]["grid"]
        self.title("Tic Tac Toe")
        self.spec = True if res["msg"] == "spec" else False
        self.current_player = 0
        self.player_names = res["data"]["players"]
        self.game_id = res["data"]["game_id"]
        self.timer_labels = []
        self.symbol = res["data"]["symbol"] if self.spec is False else None
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Tic Tac Toe", font=('Arial', 24, 'bold')).grid(row=0, columnspan=self.max_players+2)

        # Tic Tac Toe grid
        state = tk.DISABLED if self.spec else tk.NORMAL
        self.tic_tac_toe_grid = [[None for _ in range(self.max_players+1)] for _ in range(self.max_players+1)]
        for i in range(self.max_players+1):
            for j in range(self.max_players+1):
                sym = " " if self.board[i][j] == -1 else self.symbols[self.board[i][j]]
                self.tic_tac_toe_grid[i][j] = ttk.Button(self, text=sym, font=('Arial', 20), command=lambda i=i, j=j: self.move(i, j), width=5, height=2, state=state)
                self.tic_tac_toe_grid[i][j].grid(row=i+1, column=j)

        # Player list
        self.player_labels = []
        for i in range(self.num_players):
            player_name = ttk.Label(self, text=self.player_names[i], font=('Helvetica', 16))
            player_name.grid(row=i+2, column=self.max_players+2)
            self.player_labels.append(player_name)

        ttk.Button(self, text="Exit Game", command=self.exit_game).grid(row=self.max_players+2, column=0, columnspan=self.max_players+2)

    def move(self, i, j):
        self.tic_tac_toe_grid[i][j].config(text=self.symbols[self.symbol], state=tk.DISABLED)
        # self.parent.clnt.request("move", i, j)

    def exit_game(self):
        self.parent.clnt.request("exit_game", self.spec, self.game_id)

if __name__ == "__main__":
    game = App()
