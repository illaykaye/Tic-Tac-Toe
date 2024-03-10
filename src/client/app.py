import tkinter as tk
import tkinter.ttk as ttk
import clnt
import time
class App():

    def __init__(self) -> None:
        self.window = tk.Tk()
        self.clnt = clnt.Client(self.handle_response)
        self.clnt.start_client()

    
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
            elif res["msg"] in ["joined"]:
                self.game(res)
            elif res["msg"] == "spec":
                self.game(res,spec=True)
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

    def exit(self):
        self.window.destroy()
        self.window.quit()

    def start_page(self):
        self.reset_window()
        ttk.Label(self.window, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="Login", command=lambda: self.log_sign_page("login")).pack(pady=3,expand=True)
        ttk.Button(self.window,text="Signup", command=lambda: self.log_sign_page("signup")).pack(pady=1)
        ttk.Button(self.window, text='Exit', command=exit).pack(pady=3,expand=True)

        self.window.mainloop()

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
        self.window.bind("Enter",lambda: self.clnt.request(act, username.get(), password.get()))
        self.window.mainloop()
    
    def main_page(self):
        self.reset_window()
        ttk.Label(self.window, text="Welcome {}!".format(self.clnt.username), font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="New Game", command=self.new_game_page).pack(pady=3,expand=True)
        ttk.Button(self.window,text="Available Games", command=lambda: self.clnt.request("aval")).pack(pady=1)
        ttk.Button(self.window, text="Leaderboard", command=lambda: self.clnt.request("lb")).pack(pady=1,expand=True)
        ttk.Button(self.window, text='Exit', command=exit).pack(pady=3,expand=True)

        self.window.mainloop()

    def leaderboard_page(self, data):
        self.reset_window()
        ttk.Label(self.window, text="Leaderboard",font=("ubuntu",16)).pack(pady=3,expand=True)
        ttk.Label(self.window, text="Most wins: {}, {}".format(data["wins"]["username"], data["wins"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self.window, text="Most wins: {}, {}".format(data["loses"]["username"], data["loses"]["num"])).pack(pady=3,expand=True)
        ttk.Label(self.window, text="Most wins: {}, {}".format(data["draws"]["username"], data["draws"]["num"])).pack(pady=3,expand=True)
        ttk.Button(self.window, text="Back", command=self.main_page).pack(pady=3,expand=True,side="bottom")

        self.window.mainloop()

    def new_game_page(self):
        self.reset_window()
        ttk.Label(self.window, text="Choose number of players:", font=("ubuntu",14)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="2", command=lambda: self.clnt.request("new",2)).pack(pady=3,expand=True)
        ttk.Button(self.window,text="3", command=lambda: self.clnt.request("new",3)).pack(pady=1)
        ttk.Button(self.window, text="4", command=lambda: self.clnt.request("new",4)).pack(pady=1,expand=True)
        ttk.Button(self.window, text="Back", command=self.main_page).pack(pady=3,expand=True,side="bottom")


    def available_games_page(self, data):
        self.reset_window()
        ttk.Label(self.window, text="Available Games", font=("ubuntu", 16)).pack(pady=3)
        count = 1
        for game_id, game in data.items():
            game_info = f"Game: {count}, Max Players: {game['max_players']}, Players in Game: {game['num_players']}, Spectators: {game["num_spec"]}"
            if game["num_players"] == game["max_players"]:
                button_text = "Join"
                command = lambda: self.clnt.request("join", game_id)
            else:
                button_text = "Full"
                command = None
            ttk.Label(self.window, text=game_info).pack()
            ttk.Button(self.window, text=button_text).pack()
            
    
        ttk.Button(self.window,text="Back", command=self.main_page).pack(tk.BOTTOM)


    def game(self,res,spec=False):
        return 0
if __name__ == "__main__":
    game = App()
