import tkinter as tk
import tkinter.ttk as ttk
import clnt
from functools import partial

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
                self.main_page(res["data"]["username"])
            elif res["msg"] in ["joined"]:
                self.game(res)
            elif res["msg"] == "spec":
                self.game(res,spec=True)
        elif res["status"] == "info":
            if res["msg"] == "aval":
                self.available_games_page(res)
            elif res["msg"] == "lb":
                self.leaderboard_page(res)

    def new_window(self,w=300,l=350):
        self.window.destroy()
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe")
        self.window.geometry('{}x{}'.format(w,l))
        self.window.resizable(False, False)

    def exit(self):
        self.window.destroy()
        self.window.quit()

    def start_page(self):
        self.new_window()
        ttk.Label(self.window, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="Login", command=self.login_page).pack(pady=3,expand=True)
        ttk.Button(self.window,text="Signup", command=self.signup_page).pack(pady=1)
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

    def login_page(self):
        username = tk.StringVar()
        password = tk.StringVar()
        self.new_window(360,120)
        ttk.Label(self.window, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self.window, textvariable=username).place(x=130,y=10)
        ttk.Label(self.window, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self.window, textvariable=password).place(x=130,y=40)
        ttk.Button(self.window,text="Back", command=self.start_page).place(x=70,y=70)
        ttk.Button(self.window, text="Login", command=lambda: self.clnt.request("signup", username.get(), password.get())).place(x=160,y=70)
        self.window.mainloop()
        
    def signup_page(self):
        self.new_window(360,120)
        username = tk.StringVar()
        password = tk.StringVar()
        ttk.Label(self.window, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self.window, textvariable=username).place(x=130,y=10) # username entry
        ttk.Label(self.window, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self.window, textvariable=password,show="*").place(x=130,y=40) # password entry
        ttk.Button(self.window,text="Back",command=self.start_page).place(x=70,y=70)
        ttk.Button(self.window, text="Sign up",command=lambda: self.clnt.request("signup", username.get(), password.get())).place(x=160,y=70)

        self.window.mainloop()

    def main_page(self, username):
        self.new_window()
        ttk.Label(self.window, text="Welcome {}!".format(username), font=("ubuntu",16)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="New Game", command=self.new_game_page).pack(pady=3,expand=True)
        ttk.Button(self.window,text="Available Games", command=self.available_games_page).pack(pady=1)
        ttk.Button(self.window, text="Leaderboard", command=self.leaderboard_page).pack(pady=1,expand=True)
        ttk.Button(self.window, text='Exit', command=exit).pack(pady=3,expand=True)

        self.window.mainloop()

    def leaderboard_page(self):
        self.new_window()
        ttk.Label(self.window, text="Leaderboard",font=("ubuntu",16)).pack(pady=3,expand=True)
        ttk.Button(self.window, text="Home", command=self.main_page).pack(pady=3,expand=True,side="bottom")

        self.window.mainloop()

    def new_game_page(self):
        self.new_window()
        ttk.Label(self.window, text="Choose number of players:", font=("ubuntu",10)).pack(pady=2,expand=True)
        ttk.Button(self.window, text="2", command=lambda: self.clnt.request("new",2)).pack(pady=3,expand=True)
        ttk.Button(self.window,text="3", command=lambda: self.clnt.request("new",3)).pack(pady=1)
        ttk.Button(self.window, text="4", command=lambda: self.clnt.request("new",4)).pack(pady=1,expand=True)

    def available_games_page(self):
        return 0

    def game(self,res,spec=False):
        return 0
if __name__ == "__main__":
    game = App()
