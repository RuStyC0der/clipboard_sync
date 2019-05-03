from tkinter import *
from sys import exit
import socket
import pickle
import pyperclip
import threading
from time import sleep

sock = socket.socket()

work_mode = "Server_sync"

user_list = {}
old_clip = None

clip = None
clip_user = None
clip_ch_flag = None

request = None
request_user = None
request_ch_flag = None

def recive_server_controller():
    global clip, clip_ch_flag, user_list, request, request_ch_flag, clip_user, request_user
    for i in user_list:
        user_list[i][0].setblocking(0)
        try:
            data = pickle.loads((user_list[i])[0].recv(4096))
            print("data is", data)
        except:
            return
        user_list[i][0].setblocking(1)
        if data[-1] == "clip":
            print("recived clip", i)
            clip = data[0]
            clip_ch_flag = True
            clip_user = i
        elif data[-1] == "request":
            print("recived_request", i)
            request = data[0]
            request_user = i
            request_ch_flag = True

def server_sync():

    def get_myclip():
        global old_clip
        server_clip = pyperclip.paste()
        if old_clip != server_clip:
            old_clip = server_clip
            return server_clip, True
        else:
            return server_clip, False

    def add_user(work_mode, timeout=1):
        global user_list
        sock.settimeout(timeout)
        try:
            conn, addr = sock.accept()
        except:
            return
        name = pickle.loads(conn.recv(1024))
        conn.send(pickle.dumps(work_mode))
        user_list[name] = (conn, addr)

    def server_sync():
        global user_list
        sock.settimeout(None)
        server_clip, ch_flag = get_myclip()
        if ch_flag:
            print("clip changed to server clip")
            for j in user_list:
                user_list[j][0].send(pickle.dumps([server_clip, "clip"]))

    def port_bind(event):
        port = entry_port.get()
        if not port.isdigit() or int(port) in range(0, 1024):
            entry_port.delete(0, END)
            entry_port.insert(0, "Incorrect port")
            entry_port.after(1000, lambda: entry_port.delete(0, END))
            return
        entry_port.destroy()
        port_label_value = Label(text=port, bg="#33FFFF", fg="white")
        port_label_value.place(x=55, y=40)
        start_button["text"] = "Exit"
        start_button.bind("<Button-1>", func=lambda x: exit())
        status_label["text"] = "Starting server"
        status_label["bg"] = "orange"
        sock.bind(('', int(port)))
        sock.listen(10)
        work_thread.start()
        status_label["text"] = "Server started"
        status_label["bg"] = "green"


    def thread_cycle(event=0):
        global work_mode
        while True:
            add_user(work_mode)
            recive_server_controller()
            server_sync()
            sleep(1)

    work_thread = threading.Thread(target=thread_cycle)

    window = Tk()
    window.resizable(False,False)
    window.geometry("200x220")
    window.title("ALL sync mode | server")

    entry_port = Entry(width=15)
    port_label = Label(text="Port")
    start_button = Button(window, text="Start", width=17)
    status_label = Label(text="Server stopped", bg="red",height=1,width=20)
    nick_name_label = Label(text="Your nickname is Server",bg="#00CCFF",fg="white",height=1,width=20)
    ip_label = Label(text=("Your IP is {}".format(socket.gethostbyname(socket.gethostname()))), bg="#00CCFF",
                     fg="white", height=1, width=20)

    ip_label.place(x=25, y=160)
    nick_name_label.place(x=20, y=10)
    status_label.place(x=25, y=180)
    port_label.place(x=25, y=40)
    entry_port.place(x=55, y=40)
    start_button.place(x=35, y=70)


    start_button.bind("<Button-1>", func=port_bind)


    window.after(20000, lambda : window.destroy())
    window.mainloop()

server_sync()
