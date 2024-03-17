import tkinter as tk
import tkinter.ttk as ttk
import threading
import clnt

PLAYER_TIME_LIMIT = 30
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8080  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

"""
Class for managing the GUI aspect of the game.
"""
class App(tk.Tk):
    """
    Constructor method, sets up the GUI
    """
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe")
        self.geometry('550x550')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

        self.client = clnt.Client(self.handle_respone, HOST, PORT)
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.grid_rowconfigure(0, weight=1)  # Make the container fill the window vertically
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.init_frames()
        self.in_game = False
        self.client.start_client()

    """
    Create frames for each aspect of the game (Start, login, signup, etc.)
    """
    def init_frames(self):
        for F in (StartPage, LoginPage, SignupPage, MainPage, LeaderPage, AvalGamesPage, NewGamePage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid_propagate(False)

    """
    Handle responses to a socket packet.
    Depending on the status of the packet, show a specific frame.
    param packet: The data packet
    """
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
                self.in_game = False
                self.show_frame(MainPage)
            elif packet["msg"] == "left_spec":
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
        frame : ttk.Frame = self.frames.get(cont) # self.frames[cont]
        if data != None:
            frame.refresh_page(data)
            self.frames[cont] = frame
        elif cont == MainPage: frame.refresh_page()
        frame.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
        frame.grid_propagate(False)
        
        frame.tkraise()

    # init game frame
    def open_game(self, data, spec):
        frame : ttk.Frame = self.frames.get(TicTacToeGame)
        if frame != None: del self.frames[frame]
        self.frames[TicTacToeGame] = TicTacToeGame(self.container, self, data, spec)
        self.show_frame(TicTacToeGame)
        self.frames[TicTacToeGame].refresh_page(data)
        #self.frames[TicTacToeGame].timer_config(data["time_remaining"])

    """
    Request to exit the specified game.
    param game_id: The id of the game to leave
    param spec: whether or not the user is spectating
    destroy: whether or not to destroy the game
    """
    def exit_game(self, game_id, spec, destroy=False):
        self.frames[TicTacToeGame].pack_forget()
        del self.frames[TicTacToeGame]
        self.client.request("exit_game", game_id, spec, destroy)

    """
    Method to call when closing the window
    """
    def on_closing(self):
        if self.in_game:
            self.frames[TicTacToeGame].exit_game(destroy=True)
        else:
            self.destroy()

    """
    Display error message window
    """
    def err_win(self, err):
        error_win = tk.Tk()
        error_win.title("Error")
        error_win.geometry('300x60')
        inc = ttk.Label(error_win, text=err, font=("ubuntu, 14"))
        inc.config(foreground='red')
        inc.pack()

    """
    Display a generic message window
    """
    def msg_win(self, msg):
        msg_win = tk.Tk()
        msg_win.title("msg")
        msg_win.geometry('300x60')
        inc = ttk.Label(msg_win, text=msg, font=("ubuntu, 14"))
        inc.pack()

"""
Frame for startup page
"""
class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller

        ttk.Label(self, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=10)
        ttk.Button(self, text="Login", command=lambda: self.controller.show_frame(LoginPage)).pack(pady=10)
        ttk.Button(self, text="Signup", command=lambda: self.controller.show_frame(SignupPage)).pack(pady=10)
        ttk.Button(self, text="Exit", command=lambda: self.controller.on_closing()).pack(pady=10)

"""
Frame for login page
"""
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
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(StartPage)).place(x=70, y=70)
        ttk.Button(self, text="Login", command=self.login).place(x=160, y=70)

    """
    Send request to server to login.
    """
    def login(self):
        self.controller.client.request("login", self.username.get(), self.password.get())

"""
Signup page frame
"""
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

    """
    Send request to server for signup.
    """
    def signup(self):
        self.controller.client.request("signup", self.username.get(), self.password.get())

"""
Main menu frame
"""
class MainPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller

    """
    Refresh the main page
    """
    def refresh_page(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()   

    """
    Create widgets for user (welcome, new game, etc)
    """
    def create_widgets(self):
        ttk.Label(self, text="Welcome {}!".format(self.controller.client.username), font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self, text="New Game", command=lambda: self.controller.show_frame(NewGamePage)).pack(pady=3,expand=True)
        ttk.Button(self, text="Available Games", command=lambda: self.controller.client.request("aval")).pack(pady=1)
        ttk.Button(self, text="Leaderboard", command=lambda: self.controller.client.request("lb")).pack(pady=1,expand=True)
        ttk.Button(self, text="Logout", command=lambda: self.controller.client.request("logout")).pack(pady=1,expand=True)
        ttk.Button(self, text='Exit', command=lambda: self.controller.client.request("exit")).pack(pady=3,expand=True)

"""
Leaderboard frame
"""
class LeaderPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller

    """
    Refresh page with new data
    """
    def refresh_page(self, data: dict):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets(data)

    """
    Display widgets for most wins, losses, and draws
    """
    def create_widgets(self, data: dict):
        ttk.Label(self, text="Leaderboard", font=("ubuntu",16)).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["wins"]["username"], data["wins"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most loses: {}, {}".format(data["loses"]["username"], data["loses"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most draws: {}, {}".format(data["draws"]["username"], data["draws"]["num"])).pack(pady=3,expand=True)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(pady=3,expand=True,side="bottom")

"""
Frame for creating a new game
"""
class NewGamePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller
        ttk.Label(self, text="Choose number of players:", font=("ubuntu",14)).pack(pady=2,expand=True)
        ttk.Button(self, text="2", command=lambda: self.controller.client.request("new",2)).pack(pady=3,expand=True)
        ttk.Button(self, text="3", command=lambda: self.controller.client.request("new",3)).pack(pady=1)
        ttk.Button(self, text="4", command=lambda: self.controller.client.request("new",4)).pack(pady=1,expand=True)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(pady=3,expand=True,side="bottom")

"""
Frame to display available games
"""
class AvalGamesPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller : App = controller

    """
    Refresh page with new data
    """
    def refresh_page(self, data: dict):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets(data)

    """
    Create widgets for the list of available games
    param data: The data for the list of available games
    """
    def create_widgets(self, data: dict):
        ttk.Label(self, text="Available Games", font=("ubuntu", 16)).pack(pady=3)
        count = 1

        if len(data) == 0:
            # If there are no games, print so
            ttk.Label(self, text="No games available").pack(pady=3, expand=True)
        else:
            print(data)
            for game_id, game in data.items():
                # game_info = information on the game
                game_info = f"Game: {count}, Max Players: {game['max_players']}, Players in Game: {game['num_players']}"
                # If the game is not full, allow the user to join it
                if game["num_players"] < game["max_players"]:
                    button_text = "Join"
                    state = tk.NORMAL
                    command = lambda id=game_id: self.controller.client.request("join", id)
                # o/w it is full
                else:
                    button_text = "Full"
                    state = tk.DISABLED
                    command = None

                # Create widget for joining the current game
                row_frame = ttk.Frame(self)
                ttk.Label(row_frame, text=game_info).pack(side=tk.LEFT,padx=5)
                join_button = ttk.Button(row_frame, text=button_text, command=command, state=state)
                join_button.pack(side=tk.LEFT,padx=5)
                spec_button = ttk.Button(row_frame, text="Spectate", command=lambda id=game_id: self.controller.client.request("spec", id))
                spec_button.pack(side=tk.LEFT,padx=5)
                row_frame.pack()
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(side=tk.BOTTOM,pady=3)

"""
Frame for the game itself
"""
class TicTacToeGame(tk.Frame):
    def __init__(self, parent, controller, data, spec=False):
        super().__init__(parent)
        self.controller : App = controller
        self.symbols = ['x','○','△','□']
        self.spec = spec
        self.my_turn = False
        self.set_data(data)
        self.timer_timer = threading.Timer(1, lambda: self.timer_config())

        self.time_remaining = PLAYER_TIME_LIMIT
        self.timer_update = threading.Timer(0.2, lambda: self.controller.client.request("update", self.game_id))
        self.create_widgets()

    """
    Request update from server
    """
    def request_update(self):
        self.timer_update = threading.Timer(0.2, lambda: self.controller.client.request("update", self.game_id))
        self.timer_update.start()

    """
    Set data from json to object members
    """
    def set_data(self, data):
        print(data)
        self.game_id = data["game_id"]
        self.max_players = data["max_players"]
        self.num_players = data["num_players"]
        self.player_names = data["players"]
        self.left_players = data["left_players"]
        self.board = data["grid"]
        self.current_player = data["current_player"]
        self.started = data["started"]
        self.symbol = data["players"].index(self.controller.client.username) if not self.spec else None
        self.status = data["status"]
        self.my_turn = self.player_names[self.current_player] == self.controller.client.username

    """
    Refresh the current frame with new data.
    """
    def refresh_page(self, data):
        self.set_data(data)
        self.config_widgets()
        if self.started:
            if self.status != -2:
                self.declare_winner()
            elif self.my_turn:
                self.time_remaining = PLAYER_TIME_LIMIT
                self.timer_config()
            else: self.request_update()
        else: self.request_update()

    """
    Tell server current turn has ended
    """
    def turn_ended(self):
        self.timer_timer.cancel()
        self.timer_label.config(text="00:00")
        self.controller.client.request("turn_ended", self.game_id)

    """
    Write who won the game
    """
    def declare_winner(self):
        if self.status == -1:
            text = "Draw!"
        else:
            if self.player_names[self.status] == self.controller.client.username:
                text = "You won!"
            else:
                text = "{} won!".format(self.player_names[self.status])
        self.timer_timer.cancel()
        self.timer_update.cancel()
        self.spec = True
        self.config_widgets()
        self.spec = False
        self.winner_label.config(text=text)

    """
    Set up timer for displaying how much time is left.
    """
    def timer_config(self):
        self.timer_timer = threading.Timer(1, lambda: self.timer_config())
        # If the game has not started, check back in one second to see if it has
        if not self.started: self.timer_timer.start()
        else:
            # o/w if there is no time remaining, the current turn has ended
            if self.time_remaining < 0: self.turn_ended()
            # o/w print how much time is left
            else:
                minutes = int(self.time_remaining // 60)
                seconds = int(self.time_remaining % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                self.timer_label.config(text=time_str)
                # decrement the amount of time left by 1 sec
                self.time_remaining -= 1
                # start the timer again so the whole process is repeated in the next second
                self.timer_timer.start()

    """
    Configure widgets.
    """
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
                if self.player_names[i] not in self.left_players:
                    name = "{}: {}".format(self.player_names[i], self.symbols[i])
                else:
                    name = "{} left".format(self.player_names[i], self.symbols[i])
            else:
                name = " "
            self.player_labels[i].config(text=name)
        if self.started:
            if self.player_names[self.current_player] == self.controller.client.username:
                turn_text = "Your turn"
            else:
                turn_text = "{}'s turn".format(self.player_names[self.current_player])
            self.turn_label.config(text=turn_text)

    """
    Create tic tac toe grid and player list
    """
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
        ttk.Button(self, text="Exit Game", command=lambda: self.exit_game(False)).grid(row=self.max_players+3,column=0,columnspan=self.max_players)
        self.winner_label = ttk.Label(self, text="", font=("Helvetica", 20))
        self.winner_label.grid(row=self.max_players+4,column=0,columnspan=self.max_players)        

    """
    Move to the (i,j)th coordinate
    """
    def move(self, i, j):
        # Stop the timer
        self.timer_timer.cancel()
        # Set it to zero
        self.timer_label.config(text="00:00")
        # Move to the specified place
        self.tic_tac_toe_grid[i][j].config(text=self.symbols[self.symbol],state=tk.DISABLED)
        self.controller.client.request("move", self.game_id, i, j)

    """
    Add a user to the game
    """
    def add_player(self, data):
        self.num_players += 1
        player_name = tk.Label(self, text=data["username"],font=('Helvetica', 16))
        player_name.grid(row=self.num_players+1, column=self.max_players+2)

    """
    Exit the game
    """
    def exit_game(self, destroy=False):
        self.timer_timer.cancel()
        self.timer_update.cancel()
        self.controller.exit_game(self.game_id, self.spec, destroy)

if __name__ == "__main__":
    app = App()
    app.mainloop()
