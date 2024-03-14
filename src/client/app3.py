import tkinter as tk
import tkinter.ttk as ttk
import threading
import socket
import clnt
import time

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
        self.init_frames()

        self.client.start_client()
    
    def init_frames(self):
        for F in (StartPage, LoginPage, SignupPage, MainPage, LeaderPage, AvalGamesPage, NewGamePage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid_propagate(False)

    def handle_respone(self, packet):
        # error response 
        if packet["status"] == "err":
            self.err_win(packet["msg"])

        # general responses
        elif packet["status"] == "suc":
            if packet["msg"] == "connected":
                self.show_frame(StartPage)
            elif packet["msg"] == "exit":
                self.destroy()
            elif packet["msg"] == "logged":
                self.client.token = packet["data"]["token"]
                self.client.username = packet["data"]["username"]
                self.show_frame(MainPage)
            elif packet["msg"] == "logout":
                self.client.token = ''
                self.client.username = ''
                #self.init_frames()
                self.show_frame(StartPage)
            elif packet["msg"] == "signup":
                self.show_frame(StartPage)

        # data responses
        elif packet["status"] == "info":
            if packet["msg"] == "aval":
                self.show_frame(AvalGamesPage, packet["data"])
            elif packet["msg"] == "lb":
                self.show_frame(LeaderPage,packet["data"])

        # in game responses
        elif packet["status"] == "game":
            if packet["msg"] == "joined":
                print("starting game")
                self.open_game(packet["data"], packet["msg"] == "spec")
            elif packet["msg"] == "spec":
                self.open_game(packet["data"], packet["msg"] == "spec")
            elif packet["msg"] == "user_left_game":
                del self.frames[TicTacToeGame]
                self.show_frame(MainPage)
            elif packet["msg"] == "left_spec":
                del self.frames[TicTacToeGame]
                self.show_frame(MainPage)
            elif packet["msg"] == "update":
                print("updating")
                self.frames[TicTacToeGame].refresh_page(packet["data"])
            elif packet["msg"] in ["no_update", "move"]:
                self.frames[TicTacToeGame].request_update()
            elif packet["msg"] == "turn_ended":
                self.frames[TicTacToeGame].request_update()
            elif packet["msg"] == "timer":
                self.frames[TicTacToeGame].timer_config(packet["data"]["time_remaining"])

    # switch to frame (page in the GUI)
    def show_frame(self, cont, data=None):     
        for frame in self.frames.values():
            frame.pack_forget()
        frame : ttk.Frame = self.frames.get(cont)
        if data != None:
            print("okok")
            frame.refresh_page(data)
            self.frames[cont] = frame
        elif cont == MainPage: frame.refresh_page()
        frame.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
        frame.grid_propagate(False)
        
        frame.tkraise()

    # init game frame
    def open_game(self, data, spec):
        frame : ttk.Frame = self.frames.get(TicTacToeGame)
        #if frame != None: del self.frames[frame]
        self.frames[TicTacToeGame] = TicTacToeGame(self.container, self, data, spec)
        self.show_frame(TicTacToeGame)
        self.frames[TicTacToeGame].refresh_page(data)
        #self.frames[TicTacToeGame].timer_config(data["time_remaining"])


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
    
class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=10)
        ttk.Button(self, text="Login", command=lambda: controller.show_frame(LoginPage)).pack(pady=10)
        ttk.Button(self, text="Signup", command=lambda: controller.show_frame(SignupPage)).pack(pady=10)
        ttk.Button(self, text="Exit", command=lambda: controller.destroy).pack(pady=10)
    
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

    def refresh_page(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()   

    def create_widgets(self):
        ttk.Label(self, text="Welcome {}!".format(self.controller.client.username), font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self, text="New Game", command=lambda: self.controller.show_frame(NewGamePage)).pack(pady=3,expand=True)
        ttk.Button(self, text="Available Games", command=lambda: self.controller.client.request("aval")).pack(pady=1)
        ttk.Button(self, text="Leaderboard", command=lambda: self.controller.client.request("lb")).pack(pady=1,expand=True)
        ttk.Button(self, text="Logout", command=lambda: self.controller.client.request("logout")).pack(pady=1,expand=True)
        ttk.Button(self, text='Exit', command=lambda: self.controller.client.request("exit")).pack(pady=3,expand=True)

class LeaderPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller

    def refresh_page(self, data: dict):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets(data)

    def create_widgets(self, data: dict):
        ttk.Label(self, text="Leaderboard", font=("ubuntu",16)).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["wins"]["username"], data["wins"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["loses"]["username"], data["loses"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["draws"]["username"], data["draws"]["num"])).pack(pady=3,expand=True)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(pady=3,expand=True,side="bottom")

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
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller

    def refresh_page(self, data: dict):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets(data)

    def create_widgets(self, data: dict):
        ttk.Label(self, text="Available Games", font=("ubuntu", 16)).pack(pady=3)
        count = 1
        if len(data) == 0:
            ttk.Label(self, text="No games available").pack(pady=3, expand=True)
        else:
            print(data)
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
        #self.need_update = True
        self.my_turn = False
        self.set_data(data)
        self.timer_timer = threading.Timer(1, lambda: self.timer_config())

        #self.turn_ended = False
        self.time_remaining = 30
        self.timer_update = None
        self.create_widgets()


    def request_update(self):
        #self.need_update = True
        self.timer_update = threading.Timer(0.2, lambda: self.controller.client.request("update", self.game_id))
        self.timer_update.start()

    def set_data(self, data):
        print(data)
        self.game_id = data["game_id"]
        self.max_players = data["max_players"]
        self.num_players = data["num_players"]
        self.player_names = data["players"]
        self.board = data["grid"]
        self.current_player = data["current_player"]
        self.started = data["started"]
        self.symbol = data["players"].index(self.controller.client.username) if not self.spec else None
        self.status = data["status"]
        self.my_turn = self.player_names[self.current_player] == self.controller.client.username
        #self.need_update = (not self.my_turn or not self.started) or self.spec

    def refresh_page(self, data):
        self.set_data(data)
        self.config_widgets()
        if self.started:
            if self.status != -2:
                #winner_timer = threading.Timer(2, lambda: self.declare_winner())
                #winner_timer.start()
                self.declare_winner()
            elif self.my_turn:
                self.time_remaining = 30
                self.timer_config()
            else: self.request_update()
        else: self.request_update()
            

    def turn_ended(self):
        self.timer_timer.cancel()
        self.timer_label.config(text="00:00")
        self.controller.client.request("turn_ended", self.game_id)

    def declare_winner(self):
        text = "Draw!" if self.status == -1 else "{} won!".format(self.player_names[self.status])
        self.timer_timer.cancel()
        self.timer_update.cancel()
        self.spec = True
        self.config_widgets()
        self.spec = False
        self.winner_label.config(text=text)

    def timer_config(self):
        self.timer_timer = threading.Timer(1, lambda: self.timer_config())
        if not self.started: self.timer_timer.start()
        else:
            if self.time_remaining < 0: self.turn_ended()
            else:
                minutes = int(self.time_remaining // 60)
                seconds = int(self.time_remaining % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                self.timer_label.config(text=time_str)
                self.time_remaining -= 1
                self.timer_timer.start()

    def config_widgets(self):
        for i in range(self.max_players+1):
            for j in range(self.max_players+1):
                state = tk.DISABLED
                if self.board[i][j] == -1:
                    sym = " "
                    if self.player_names[self.current_player] == self.controller.client.username and self.started and not self.spec:
                        state = tk.NORMAL
                else:
                    sym = self.symbols[self.board[i][j]]
                    state = tk.DISABLED
                self.tic_tac_toe_grid[i][j].config(text=sym, state=state)
        for i in range(self.max_players):
            if i < self.num_players:
                name = self.player_names[i]
            else:
                name = " "
            self.player_labels[i].config(text=name)
        if self.started:
            if self.player_names[self.current_player] == self.controller.client.username:
                turn_text = "Your turn"
            else:
                turn_text = "{}'s turn".format(self.player_names[self.current_player])
            self.turn_label.config(text=turn_text)

    def create_widgets(self):
        # Tic Tac Toe grid
        #state = tk.DISABLED if self.spec else tk.NORMAL
        self.tic_tac_toe_grid = [[None for _ in range(self.max_players+1)] for _ in range(self.max_players+1)]
        for i in range(self.max_players+1):
            for j in range(self.max_players+1):
                sym = " " #if self.board[i][j] == -1 else self.symbols[self.board[i][j]]
                self.tic_tac_toe_grid[i][j] = tk.Button(self, text=sym, font=('Arial', 20), command=lambda i=i, j=j: self.move(i,j), width=5, height=2, state=tk.DISABLED)
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
        self.timer_label = tk.Label(self, text="00:00", font=('Arial', 16))
        self.timer_label.grid(row=self.max_players+2, column=self.max_players+2)
        self.turn_label = tk.Label(self, text="Game not started", font=('Helvetica', 16))
        self.turn_label.grid(row=self.max_players+2, column=0, columnspan=self.max_players)
        ttk.Button(self, text="Exit Game", command=lambda: self.exit_game()).grid(row=self.max_players+3,column=0,columnspan=self.max_players)
        self.winner_label = ttk.Label(self, text="", font=("Helvetica", 20))
        self.winner_label.grid(row=self.max_players+4,column=0,columnspan=self.max_players)        

    def move(self, i, j):
        self.timer_timer.cancel()
        self.timer_label.config(text="00:00")
        self.tic_tac_toe_grid[i][j].config(text=self.symbols[self.symbol],state=tk.DISABLED)
        self.controller.client.request("move", self.game_id, i, j)
    
    def add_player(self, data):
        self.num_players += 1
        player_name = tk.Label(self, text=data["username"],font=('Helvetica', 16))
        player_name.grid(row=self.num_players+1, column=self.max_players+2)

    def exit_game(self):
        self.timer_timer.cancel()
        self.timer_update.cancel()

        self.controller.client.request("exit_game", self.game_id, self.spec)

if __name__ == "__main__":
    app = App()
    app.mainloop()
