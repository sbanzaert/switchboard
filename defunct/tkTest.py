import tkinter as tk
from time import sleep
root = tk.Tk()

root.geometry("{0}x{1}+0+0".format(int(root.winfo_screenwidth()/2), int(root.winfo_screenheight()/2)))
root.bind("<Button-1>", lambda evt: root.destroy())

l = tk.Label(text="TESTING", font=("Helvetica", 120))
l.pack(expand=True)

root.update()
sleep(5)
l.config(text=200, fg='red')
root.update()
sleep(2)
