import tkinter as tk
import tkinter.ttk as ttk
import clnt
import time
class App():

    def __init__(self) -> None:
        self.window = tk.Tk()
        self.clnt = clnt.Client(self.handle_response)
        self.clnt.start_client()
        self.window.mainloop()
    
    def handle_response(self, res):
        if res["status"] == "err":
            self.err_win(res["msg"])
        elif res["status"] == "suc":
            if res["msg"] == "connected":
                self.start_page()
            elif res["msg"] == "logged":
                self.clnt.token = res["data"]["token"]
                self.clnt.username = res["data"]["username"]
                self.main_page()
            elif res["msg"] == "signup":
                self.start_page()
            elif res["msg"] in ["joined", "spec"]:
                self.clnt.game_id = res["data"]["game_id"]
                self.game(res)
        elif res["status"] == "info":
            if res["msg"] == "aval":
                self.available_games_page(res["data"])
            elif res["msg"] == "lb":
                self.leaderboard_page(res["data"])

    def reset_window(self,w=300,l=350):
        for widget in self.window.winfo_children():
            widget.destroy()
        self.window.title("Tic Tac Toe")
        self.window.geometry('{}x{}'.format(w,l))
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def exit(self):
        self.on_closing()
        self.window.destroy()
        self.window.quit()

    def start_page(self):
        self.reset_window()
        ttk.Label(self.window, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="Login", command=lambda: self.log_sign_page("login")).pack(pady=3,expand=True)
        ttk.Button(self.window,text="Signup", command=lambda: self.log_sign_page("signup")).pack(pady=1)
        ttk.Button(self.window, text='Exit', command=exit).pack(pady=3,expand=True)

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

    def log_sign_page(self, act):
        if act == "login": button = "Login"
        else: button = "Signup"
        username = tk.StringVar()
        password = tk.StringVar()
        self.reset_window()
        ttk.Label(self.window, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self.window, textvariable=username).place(x=130,y=10)
        ttk.Label(self.window, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self.window, textvariable=password,show="*").place(x=130,y=40)
        ttk.Button(self.window,text="Back", command=self.start_page).place(x=70,y=70)
        ttk.Button(self.window, text=button, command=lambda: self.clnt.request(act, username.get(), password.get())).place(x=160,y=70)
        
    
    def main_page(self):
        self.reset_window()
        ttk.Label(self.window, text="Welcome {}!".format(self.clnt.username), font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="New Game", command=self.new_game_page).pack(pady=3,expand=True)
        ttk.Button(self.window,text="Available Games", command=lambda: self.clnt.request("aval")).pack(pady=1)
        ttk.Button(self.window, text="Leaderboard", command=lambda: self.clnt.request("lb")).pack(pady=1,expand=True)
        ttk.Button(self.window, text='Exit', command=exit).pack(pady=3,expand=True)


    def leaderboard_page(self, data):
        self.reset_window()
        ttk.Label(self.window, text="Leaderboard",font=("ubuntu",16)).pack(pady=3,expand=True)
        ttk.Label(self.window, text="Most wins: {}, {}".format(data["wins"]["username"], data["wins"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self.window, text="Most wins: {}, {}".format(data["loses"]["username"], data["loses"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self.window, text="Most wins: {}, {}".format(data["draws"]["username"], data["draws"]["num"])).pack(pady=3,expand=True)
        ttk.Button(self.window, text="Back", command=self.main_page).pack(pady=3,expand=True,side="bottom")


    def new_game_page(self):
        self.reset_window()
        ttk.Label(self.window, text="Choose number of players:", font=("ubuntu",14)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="2", command=lambda: self.clnt.request("new",2)).pack(pady=3,expand=True)
        ttk.Button(self.window,text="3", command=lambda: self.clnt.request("new",3)).pack(pady=1)
        ttk.Button(self.window, text="4", command=lambda: self.clnt.request("new",4)).pack(pady=1,expand=True)
        ttk.Button(self.window, text="Back", command=self.main_page).pack(pady=3,expand=True,side="bottom")


    def available_games_page(self, data):
        self.reset_window(500,400)
        ttk.Label(self.window, text="Available Games", font=("ubuntu", 16)).pack(pady=3)
        count = 1
        frame = tk.Frame(self.window)
        if len(data) == 0:
            frame.pack()
            ttk.Label(frame, text="No games available").grid(row=0, column=0, columnspan=1)
            count += 1
        for game_id, game in data.items():
            game_info = f"Game: {count}, Max Players: {game['max_players']}, Players in Game: {game['num_players']}, Spectators: {game["num_spec"]}"
            if game["num_players"] < game["max_players"]:
                button_text = "Join"
                state = tk.NORMAL
                command = lambda: self.clnt.request("join", game_id)
            else:
                button_text = "Full"
                command = None
                state = tk.DISABLED
            
            frame.pack()

            label = tk.Label(frame, text=game_info)
            label.grid(row=count-1, column=0, padx=5, pady=5)

            join_button = tk.Button(frame, text=button_text, command=command, state=state)
            join_button.grid(row=count-1, column=1, padx=5, pady=5)

            join_button = tk.Button(frame, text="Spectate", command=lambda: self.clnt.request("spec", game_id))
            join_button.grid(row=count-1, column=2, padx=5, pady=5)

            count += 1
            
    
        ttk.Button(frame,text="Back", command=self.main_page).grid(row=count-1, column=0, columnspan=3, padx=5, pady=5)


    def game(self,data):
        self.window.destroy()
        self.window = TicTacToeGame(data, self)

    def on_closing(self):
        self.clnt.request("exit")
    
class TicTacToeGame(tk.Tk):
    
    def __init__(self, res, app: App):
        super().__init__()
        self.symbols = ['x','○','△','□']
        self.max_players = res["data"]["max_players"]
        self.num_players = res["data"]["num_players"]
        self.board = res["data"]["grid"]
        self.title_label = tk.Label(self, text="Tic Tac Toe", font=('Arial', 24, 'bold'))
        self.title_label.grid(row=0, columnspan=self.max_players+2)
        self.title("Tic Tac Toe")
        self.spec = True if res["msg"] == "spec" else False
        self.current_player = 0
        self.player_names = res["data"]["players"]
        self.app = app
        self.game_id = res["data"]["game_id"]
        self.timer_labels = []
        self.symbol = res["data"]["symbol"] if self.spec is False else None 
        self.create_widgets()

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
        for i in range(self.num_players):
            player_name = tk.Label(self, text=self.player_names[i],font=('Helvetica', 16))
            player_name.grid(row=i+1, column=self.max_players+2)
            self.player_labels.append(player_name)
        ttk.Button(self, text="Exit Game", command=self.exit_game).grid(row=self.max_players+2,column=0,columnspan=self.max_players+2)
    
    def player_added(self, data):
        player_name = ttk.Label(self, text=data["username"])
        player_name.grid(row=self.num_players+1, column=self.max_players+1)
        self.player_labels.append(data["username"])
    
    def move(self,i,j):
        self.tic_tac_toe_grid[i][j].config(text=self.symbols[self.symbol],state=tk.DISABLED)
        self.app.clnt.request("move", i, j)
    def exit_game(self):
        self.app.clnt.request("exit_game",self.spec, self.game_id)


if __name__ == "__main__":
    game = App()
