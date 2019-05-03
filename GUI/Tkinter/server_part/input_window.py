from tkinter import *

root = Tk()
root.resizable(False,False)
root.geometry("200x150")
root.title("Choice mode")

A_t_A_button = Button(text="All-to-All mode",bd=5)
S_S_button = Button(text="Server sync mode",bd=5)
A_S_button = Button(text="All sync mode",bd=5)

A_t_A_button.pack(expand=1)
S_S_button.pack(expand=1)
A_S_button.pack(expand=1)

root.mainloop()