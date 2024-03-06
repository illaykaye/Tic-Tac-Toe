import tkinter as tk
import tkinter.ttk as ttk
import clnt
from functools import partial

class App():

    def __init__(self) -> None:
        self.window = tk.Tk()
        self.clnt = clnt.Client()
        self.start_page()

        self.window.mainloop()
    
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

    def login_page(self):
        username = tk.StringVar()
        password = tk.StringVar()
        self.new_window(300,120)
        ttk.Label(self.window, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self.window, textvariable=username).place(x=130,y=10)
        ttk.Label(self.window, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self.window, textvariable=password).place(x=130,y=40)
        ttk.Button(self.window,text="Back", command=self.start_page).place(x=70,y=70)
        req = partial(self.clnt.request,username,password)
        ttk.Button(self.window, text="Login", command=req).place(x=160,y=70)
        self.err_win("Username or password incorrect")
        self.window.mainloop()
        
    def signup_page(self):
        username = tk.StringVar()
        password = tk.StringVar()
        self.new_window(300,120)
        ttk.Label(self.window, text="Username:", font=("ubuntu, 12")).place(x=40, y=10)
        ttk.Entry(self.window, textvariable=username).place(x=130,y=10)
        ttk.Label(self.window, text="Password:", font=("ubuntu, 12")).place(x=40, y=40)
        ttk.Entry(self.window, textvariable=password).place(x=130,y=40)
        ttk.Button(self.window,text="Back",command=self.start_page).place(x=70,y=70)
        req = partial(self.clnt.request,username,password)
        ttk.Button(self.window, text="Sign up",command=req).place(x=160,y=70)

        self.window.mainloop()

    def main_page(self):
        self.new_window()
        ttk.Label(self.window, text="Tic Tac Toe", font=("ubuntu",16)).pack(pady=2,expand=True)
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
        ttk.Button(self.window, text="2", command=self.clnt.request("new",2)).pack(pady=3,expand=True)
        ttk.Button(self.window,text="3", command=self.clnt.request("new",3)).pack(pady=1)
        ttk.Button(self.window, text="4", command=self.clnt.request("new",4)).pack(pady=1,expand=True)

    def act_recv(self):
        return 0

    def available_games_page(self):
        return 0

if __name__ == "__main__":
    game = App()
