import tkinter as tk
import tkinter.ttk as ttk
import clnt
import time

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe")
        self.geometry('300x350')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.client = clnt.Client(self.handle_response)
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.grid_rowconfigure(0, weight=1)  # Make the container fill the window vertically
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, LoginPage, SignupPage, NewGamePage):
            frame = F(self.container, self)
            self.frames[F] = frame
            #frame.pack(fill=tk.BOTH,expand=True)
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

    def handle_response(self, res):
        if res["status"] == "err":
            self.err_win(res["msg"])
        elif res["status"] == "suc":
            if res["msg"] == "connected":
                self.show_frame(StartPage)
            elif res["msg"] == "logged":
                self.client.token = res["data"]["token"]
                self.client.username = res["data"]["username"]
                self.show_frame(MainPage)
            elif res["msg"] == "signup":
                self.show_frame(StartPage)
            elif res["msg"] in ["joined", "spec"]:
                self.client.game_id = res["data"]["game_id"]
                self.show_frame(TicTacToeGame, res)
            elif res["msg"] == "user_left_game":
                self.show_frame(MainPage)
        elif res["status"] == "info":
            if res["msg"] == "aval":
                self.show_frame(AvalGamesPage, res["data"])
            elif res["msg"] == "lb":
                self.show_frame(LeaderPage,res["data"])
    
class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=10)
        ttk.Button(self, text="Login", command=lambda: controller.show_frame(LoginPage)).pack(pady=10)
        ttk.Button(self, text="Signup", command=lambda: controller.show_frame(SignupPage)).pack(pady=10)
        ttk.Button(self, text="Exit", command=controller.destroy).pack(pady=10)
    
class LoginPage(ttk.Frame):
    def __init__(self, paernt, controller: App):
        super().__init__(paernt)
        self.controller = controller
        username = tk.StringVar()
        password = tk.StringVar()
        ttk.Label(self, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self, textvariable=username).place(x=130,y=10)
        ttk.Label(self, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self, textvariable=password,show="*").place(x=130,y=40)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(StartPage)).place(x=70,y=70)
        ttk.Button(self, text="Login", command=lambda: self.controller.client.request("login", username.get(), password.get())).place(x=160,y=70)

class SignupPage(ttk.Frame):
    def __init__(self, paernt, controller: App):
        super().__init__(paernt)
        self.controller = controller
        username = tk.StringVar()
        password = tk.StringVar()
        ttk.Label(self, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self, textvariable=username).place(x=130,y=10)
        ttk.Label(self, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self, textvariable=password,show="*").place(x=130,y=40)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(StartPage)).place(x=70,y=70)
        ttk.Button(self, text="Signup", command=lambda: self.controller.client.request("signup", username.get(), password.get())).place(x=160,y=70)
        
class MainPage(ttk.Frame):
    def __init__(self, paernt, controller: App):
        super().__init__(paernt)
        self.controller = controller
        ttk.Label(self, text="Welcome {}!".format(self.controller.client.username), font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self, text="New Game", command=lambda: self.controller.show_frame(NewGamePage)).pack(pady=3,expand=True)
        ttk.Button(self,text="Available Games", command=lambda: self.controller.client.request("aval")).pack(pady=1)
        ttk.Button(self, text="Leaderboard", command=lambda: self.controller.client.request("lb")).pack(pady=1,expand=True)
        ttk.Button(self, text='Exit', command=exit).pack(pady=3,expand=True)
    
class LeaderPage(ttk.Frame):
    def __init__(self, paernt, controller: App, data):
        super().__init__(paernt)
        self.controller = controller
        ttk.Label(self, text="Leaderboard",font=("ubuntu",16)).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["wins"]["username"], data["wins"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["loses"]["username"], data["loses"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self, text="Most wins: {}, {}".format(data["draws"]["username"], data["draws"]["num"])).pack(pady=3,expand=True)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(pady=3,expand=True,side="bottom")
    
class NewGamePage(ttk.Frame):
    def __init__(self, paernt, controller: App):
        super().__init__(paernt)
        self.controller = controller
        ttk.Label(self, text="Choose number of players:", font=("ubuntu",14)).pack(pady=2,expand=True)
        ttk.Button(self, text="2", command=lambda: self.controller.client.request("new",2)).pack(pady=3,expand=True)
        ttk.Button(self,text="3", command=lambda: self.controller.client.request("new",3)).pack(pady=1)
        ttk.Button(self, text="4", command=lambda: self.controller.client.request("new",4)).pack(pady=1,expand=True)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(MainPage)).pack(pady=3,expand=True,side="bottom")

class AvalGamesPage(ttk.Frame):
    def __init__(self, parent, controller: App, data):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Available Games", font=("ubuntu", 16)).pack(pady=3)
        self.controller.geometry("500x500") 
        print(data)
        count = 1
        if len(data) == 0:
            ttk.Label(self, text="No games available").pack(pady=3)
        else:
            for game_id, game in data.items():
                game_info = f"Game: {count}, Max Players: {game['max_players']}, Players in Game: {game['num_players']}, Spectators: {game['num_spec']}"
                count += 1
                if game["num_players"] < game["max_players"]:
                    button_text = "Join"
                    state = tk.NORMAL
                    command = lambda id=game_id: self.controller.client.request("join", id)
                else:
                    button_text = "Full"
                    command = None
                    state = tk.DISABLED

                ttk.Label(self, text=game_info).pack(side=tk.LEFT, padx=5, pady=5)
                ttk.Button(self, text=button_text, command=command, state=state).pack(side=tk.LEFT, padx=5, pady=5)
                ttk.Button(self, text="Spectate", command=lambda id=game_id: self.controller.client.request("spec", id)).pack(side=tk.LEFT, padx=5, pady=5)

                ttk.Frame(self).pack(fill=tk.X, padx=5, pady=2)  # Separator between game entries
                count += 1
        
        ttk.Button(self, text="Back", command=lambda: controller.show_frame(MainPage)).pack(side=tk.BOTTOM,padx=5,pady=5)
'''
class AvalGamesPage(ttk.Frame):
    def __init__(self, paernt, controller: App, data):
        super().__init__(paernt)
        self.controller = controller
        ttk.Label(self, text="Available Games", font=("ubuntu", 16)).pack(pady=3)
        count = 1
        
        if len(data) == 0:
            ttk.Label(self, text="No games available").grid(row=0, column=0, columnspan=1)
            count += 1
        for game_id, game in data.items():
            game_info = f"Game: {count}, Max Players: {game['max_players']}, Players in Game: {game['num_players']}, Spectators: {game["num_spec"]}"
            if game["num_players"] < game["max_players"]:
                button_text = "Join"
                state = tk.NORMAL
                command = lambda: self.controller.client.request("join", game_id)
            else:
                button_text = "Full"
                command = None
                state = tk.DISABLED

            label = tk.Label(self, text=game_info)
            label.grid(row=count-1, column=0, padx=5, pady=5)

            join_button = tk.Button(self, text=button_text, command=command, state=state)
            join_button.grid(row=count-1, column=1, padx=5, pady=5)

            join_button = tk.Button(self, text="Spectate", command=lambda: self.controller.client.request("spec", game_id))
            join_button.grid(row=count-1, column=2, padx=5, pady=5)

            count += 1
            
    
        ttk.Button(self,text="Back", command=lambda: self.controller.show_frame(MainPage)).grid(row=count-1, column=0, columnspan=3, padx=5, pady=5)
'''
class TicTacToeGame(tk.Tk):
    def __init__(self, parent, controller: App, res):
        super().__init__(parent)
        self.controller = controller
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
        ttk.Button(self, text="Exit Game", command=lambda: self.exit_game).grid(row=self.max_players+2,column=0,columnspan=self.max_players+2)
    
    def player_added(self, data):
        player_name = ttk.Label(self, text=data["username"])
        player_name.grid(row=self.num_players+1, column=self.max_players+1)
        self.player_labels.append(data["username"])
    
    def move(self,i,j):
        self.tic_tac_toe_grid[i][j].config(text=self.symbols[self.symbol],state=tk.DISABLED)
        #self.app.clnt.request("move", i, j)
    def exit_game(self):
        self.controller.client.request("exit_game",self.spec, self.game_id)

if __name__ == "__main__":
    app = App()
    app.mainloop()