import tkinter as tk
import tkinter.ttk as ttk
import threading
import socket
import clnt

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe")
        self.geometry('500x500')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.client = clnt.Client(self.handle_respone)
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.grid_rowconfigure(0, weight=1)  # Make the container fill the window vertically
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, LoginPage, SignupPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid_propagate(False)

        self.client.start_client()
    
    def show_frame(self, cont, *args, **kwargs):
        for frame in self.frames.values():
            frame.pack_forget()
        frame = self.frames.get(cont)
        if frame is None:
            frame = cont(self.container, self, *args, **kwargs)
            self.frames[cont] = frame
        frame.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
        frame.grid_propagate(False)
        
        frame.tkraise()

    def on_closing(self):
        self.destroy()

    def err_win(self, err):
        error_win = tk.Tk()
        error_win.title("Error")
        error_win.geometry('300x60')
        inc = ttk.Label(error_win, text=err, font=("ubuntu, 14"))
        inc.config(foreground='red')
        inc.pack()

    def msg_win(self, msg):
        msg_win = tk.Tk()
        msg_win.title("msg")
        msg_win.geometry('300x60')
        inc = ttk.Label(msg_win, text=msg, font=("ubuntu, 14"))
        inc.pack()

    def handle_respone(self, packet):
        if packet["status"] == "err":
            self.err_win(packet["msg"])
        elif packet["status"] == "suc":
            if packet["msg"] == "connected":
                self.show_frame(StartPage)
            elif packet["msg"] == "logged":
                self.client.token = packet["data"]["token"]
                self.client.username = packet["data"]["username"]
                self.show_frame(MainPage)
            elif packet["msg"] == "signup":
                self.show_frame(StartPage)
            elif packet["msg"] in ["joined", "spec"]:
                self.client.game_id = packet["data"]["game_id"]
                self.show_frame(TicTacToeGame, packet)
            elif packet["msg"] == "user_left_game":
                self.show_frame(MainPage)
        elif packet["status"] == "info":
            if packet["msg"] == "aval":
                self.show_frame(AvalGamesPage, packet["data"])
            elif packet["msg"] == "lb":
                self.show_frame(LeaderPage,packet["data"])
        elif packet["status"] == "game":
            if packet["msg"] == "joined":
                print("starting game")
                self.show_frame(TicTacToeGame, packet["data"])
            elif packet["msg"] == "spec":
                self.show_frame(TicTacToeGame, packet["data"], True)
            elif packet["msg"] == "new_user":
                self.frames[TicTacToeGame].add_player(packet["data"])
            elif packet["msg"] == "move":
                self.frames[TicTacToeGame].move_made(packet["data"])
    
class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=10)
        ttk.Button(self, text="Login", command=lambda: controller.show_frame(LoginPage)).pack(pady=10)
        ttk.Button(self, text="Signup", command=lambda: controller.show_frame(SignupPage)).pack(pady=10)
        ttk.Button(self, text="Exit", command=controller.destroy).pack(pady=10)
    
class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller 
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(self, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self, textvariable=self.username).place(x=130, y=10)
        ttk.Label(self, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self, textvariable=self.password, show="*").place(x=130, y=40)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage)).place(x=70, y=70)
        ttk.Button(self, text="Login", command=self.login).place(x=160, y=70)

    def login(self):
        self.controller.client.request("login", self.username.get(), self.password.get())

class SignupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(self, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self, textvariable=self.username).place(x=130, y=10)
        ttk.Label(self, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self, textvariable=self.password, show="*").place(x=130, y=40)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage)).place(x=70, y=70)
        ttk.Button(self, text="Signup", command=self.signup).place(x=160, y=70)
        
    def signup(self):
        self.controller.client.request("signup", self.username.get(), self.password.get())
        
class MainPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller
        ttk.Label(self, text="Welcome {}!".format(self.controller.client.username), font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self, text="New Game", command=lambda: controller.show_frame(NewGamePage)).pack(pady=3,expand=True)
        ttk.Button(self, text="Available Games", command=lambda: controller.client.request("aval")).pack(pady=1)
        ttk.Button(self, text="Leaderboard", command=lambda: controller.client.request("lb")).pack(pady=1,expand=True)
        ttk.Button(self, text='Exit', command=controller.destroy).pack(pady=3,expand=True)

class LeaderPage(ttk.Frame):
    def __init__(self, parent, controller, data):
        super().__init__(parent)
        self.controller : App = controller
        ttk.Label(self, text="Leaderboard", font=("ubuntu",16)).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["wins"]["username"], data["wins"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["loses"]["username"], data["loses"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["draws"]["username"], data["draws"]["num"])).pack(pady=3,expand=True)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame(MainPage)).pack(pady=3,expand=True,side="bottom")

class NewGamePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller
        ttk.Label(self, text="Choose number of players:", font=("ubuntu",14)).pack(pady=2,expand=True)
        ttk.Button(self, text="2", command=lambda: self.controller.client.request("new",2)).pack(pady=3,expand=True)
        ttk.Button(self, text="3", command=lambda: self.controller.client.request("new",3)).pack(pady=1)
        ttk.Button(self, text="4", command=lambda: self.controller.client.request("new",4)).pack(pady=1,expand=True)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(pady=3,expand=True,side="bottom")

class AvalGamesPage(ttk.Frame):
    def __init__(self, parent, controller, data: dict):
        super().__init__(parent)
        self.controller : App = controller
        ttk.Label(self, text="Available Games", font=("ubuntu", 16)).pack(pady=3)
        count = 1
        if len(data) == 0:
            ttk.Label(self, text="No games available").pack(pady=3, expand=True)
        else:
            for game_id, game in data.items():
                game_info = f"Game: {count}, Max Players: {game['max_players']}, Players in Game: {game['num_players']}, Spectators: {game['num_spec']}"
                if game["num_players"] < game["max_players"]:
                    button_text = "Join"
                    state = tk.NORMAL
                    command = lambda id=game_id: self.controller.client.request("join", id)
                else:
                    button_text = "Full"
                    state = tk.DISABLED
                    command = None
                row_frame = ttk.Frame(self)
                ttk.Label(row_frame, text=game_info).pack(side=tk.LEFT,padx=5)
                join_button = ttk.Button(row_frame, text=button_text, command=command, state=state)
                join_button.pack(side=tk.LEFT,padx=5)
                spec_button = ttk.Button(row_frame, text="Spectate", command=lambda id=game_id: self.controller.client.request("spec", id))
                spec_button.pack(side=tk.LEFT,padx=5)
                row_frame.pack()
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(side=tk.BOTTOM,pady=3)


class TicTacToeGame(tk.Frame):
    def __init__(self, parent, controller, data, spec=False):
        super().__init__(parent)
        self.controller : App = controller
        self.symbols = ['x','○','△','□']

        self.spec = spec

        self.game_id = data["game_id"]
        self.max_players = data["max_players"]
        self.num_players = data["num_players"]
        self.player_names = data["players"]
        self.board = data["grid"]
        self.current_player = data["current_player"]
        
        self.symbol = data["players"].index(self.controller.client.username) if not self.spec else None
        
        self.create_widgets()

    def update_game(self, data):
        self.game_id = data["game_id"]
        self.max_players = data["max_players"]
        self.num_players = data["num_players"]
        self.player_names = data["players"]
        self.board = data["grid"]
        self.current_player = data["current_player"]
        
        self.symbol = data["players"].index(self.controller.client.username) if not self.spec else None
        self.config_widgets()

    def config_widgets(self):
        for i in range(self.max_players+1):
            for j in range(self.max_players+1):
                if self.board == -1:
                    sym = " "
                    state = tk.DISABLED if self.spec or self.player_names[self.current_player] != self.controller.client.username else tk.NORMAL
                else:
                    sym = self.symbols[self.board[i][j]]
                    state = tk.DISABLED
                self.tic_tac_toe_grid[i][j].config(text=sym, state=state)
        for i in range(self.max_players):
            if i<= self.num_players:
                name = self.player_names[i]
            else:
                name = " "
            self.player_labels.config(text=name)
    '''
    def update_timer(self, data):
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=time_str)
    '''
    def create_widgets(self):
        # Tic Tac Toe grid
        state = tk.DISABLED if self.spec else tk.NORMAL
        self.tic_tac_toe_grid = [[None for _ in range(self.max_players+1)] for _ in range(self.max_players+1)]
        for i in range(self.max_players+1):
            for j in range(self.max_players+1):
                sym = " " if self.board[i][j] == -1 else self.symbols[self.board[i][j]]
                self.tic_tac_toe_grid[i][j] = tk.Button(self, text=sym, font=('Arial', 20), command=lambda i=i, j=j: self.move(i,j), width=5, height=2, state=state)
                self.tic_tac_toe_grid[i][j].grid(row=i, column=j)

        # Player list
        self.player_labels = []
        for i in range(self.max_players):
            print(self.player_names)

            if i < self.num_players:
                name = self.player_names[i]
            else:
                name = " "
            player_name = tk.Label(self, text=name,font=('Helvetica', 16))
            player_name.grid(row=i+1, column=self.max_players+2)
            self.player_labels.append(player_name)
        ttk.Button(self, text="Exit Game", command=self.exit_game).grid(row=self.max_players+2,column=0,columnspan=self.max_players)
        self.timer_label = tk.Label(self, text="00:00", font=('Arial', 12))
        self.timer_label.grid(row=self.max_players+2, column=self.max_players+1)

    def move(self, i, j):
        self.tic_tac_toe_grid[i][j].config(text=self.symbols[self.symbol],state=tk.DISABLED)
        self.controller.client.request("move", self.game_id, i, j)
    
    def add_player(self, data):
        self.num_players += 1
        player_name = tk.Label(self, text=data["username"],font=('Helvetica', 16))
        player_name.grid(row=self.num_players+1, column=self.max_players+2)

    def move_made(self, data):
        self.tic_tac_toe_grid[data["i"]]

    def exit_game(self):
        self.controller.client.request("exit_game", self.spec, self.game_id)

if __name__ == "__main__":
    app = App()
    app.mainloop()
