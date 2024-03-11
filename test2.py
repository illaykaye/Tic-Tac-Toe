import tkinter as tk
import threading

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        
        self.remaining_time = 30
        self.label = tk.Label(root, text=f"{self.remaining_time} seconds")
        self.label.pack()

        self.timer_thread = threading.Timer(30, self.update_timer)
        self.timer_thread.start()

    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            self.label.config(text=f"{self.remaining_time} seconds")
            self.timer_thread = threading.Timer(1, self.update_timer)
            self.timer_thread.start()
        else:
            self.label.config(text="Time's up!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()