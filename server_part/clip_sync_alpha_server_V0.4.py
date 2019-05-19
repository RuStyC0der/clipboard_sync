# coding=utf-8
from tkinter import Tk, Entry, Button, Label, END, Listbox
from sys import exit
from time import sleep
from socket import socket
import pickle
import pyperclip
from threading import Thread

sock = socket()

work_mode = "All-to-All"

user_list = {}

clip = None
old_clip = None
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


def A_t_a_mode(event=0):
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
        lbox.insert(0, name)

    def all_to_all_send_recv():
        global clip, clip_ch_flag, user_list, request, request_ch_flag, clip_user, request_user
        if request_ch_flag:
            request_ch_flag = False
            if request != "user_list_get":
                if request == "server":
                    user_list[request_user][0].send(pickle.dumps([pyperclip.paste(), "clip"]))
                    return

                user_list[request][0].send(pickle.dumps(["get_clip", "request"]))
                while True:
                    if clip_ch_flag:
                        clip_ch_flag = False
                        user_list[request_user][0].send(pickle.dumps([clip, "clip"]))
                        break
            else:
                user_list[request_user][0].send(pickle.dumps([[i for i in user_list] + ["server"], "user_list"]))
                print("user list send")

    def server_get_clip(event):
        global clip, clip_ch_flag, user_list, request, request_ch_flag, clip_user, request_user
        try:
            name = lbox.get(lbox.curselection())
        except:
            return
        print(user_list)
        user_list[name][0].send(pickle.dumps(["get_clip", "request"]))
        while True:
            if clip_ch_flag:
                clip_ch_flag = False
                pyperclip.copy(clip)
                print("clip pasted to clip", name)
                break
            sleep(0.1)

    def entry_bind(event):
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
            all_to_all_send_recv()
            sleep(1)

    work_thread = Thread(target=thread_cycle)
    work_thread.daemon = True
    root.destroy()
    window = Tk()
    window.resizable(False, False)
    window.geometry("400x220")
    window.title("A-t-A mode | server")

    get_clip_button = Button(window, text="Get Clipboard")
    lbox = Listbox(width=20, height=10)
    entry_port = Entry(width=15)
    port_label = Label(text="Port")
    start_button = Button(window, text="Start", width=17)
    status_label = Label(text="Server stopped", bg="red", height=1, width=20)
    nick_name_label = Label(text="Your nickname is Server", bg="#00CCFF", fg="white", height=1, width=20)
    ip_label = Label(text=("Your IP is {}".format(socket.gethostbyname(socket.gethostname()))), bg="#00CCFF",
                     fg="white", height=1, width=20)

    ip_label.place(x=25, y=160)
    nick_name_label.place(x=25, y=10)
    status_label.place(x=25, y=180)
    port_label.place(x=25, y=40)
    entry_port.place(x=55, y=40)
    start_button.place(x=25, y=70)
    lbox.place(x=250, y=10)
    get_clip_button.place(x=270, y=180)

    start_button.bind("<Button-1>", func=entry_bind)
    get_clip_button.bind("<Button-1>", func=server_get_clip)


    window.mainloop()

def server_sync(event=0):

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

    work_thread = Thread(target=thread_cycle)
    root.destroy()
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



    window.mainloop()

def all_sync(event=0):
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
        print(name, "connected from ip", addr[0])

    def all_sync():
        global user_list, clip, clip_user, clip_ch_flag
        global old_clip
        server_clip, ch_flag = get_myclip()
        if ch_flag:
            print("clip changed to server clip")
            for j in user_list:
                user_list[j][0].send(pickle.dumps([server_clip, "clip"]))
            return
        if clip_ch_flag:
            clip_ch_flag = False
            print("clip changed to ", clip_user, " clip")
            for j in user_list:
                user_list[j][0].send(pickle.dumps([clip, "clip"]))

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
            all_sync()
            sleep(1)

    work_thread = Thread(target=thread_cycle)
    root.destroy()
    window = Tk()
    window.resizable(False, False)
    window.geometry("200x220")
    window.title("Server sync mode | server")

    entry_port = Entry(width=15)
    port_label = Label(text="Port")
    start_button = Button(window, text="Start", width=17)
    status_label = Label(text="Server stopped", bg="red", height=1, width=20)
    nick_name_label = Label(text="Your nickname is Server", bg="#00CCFF", fg="white", height=1, width=20)
    ip_label = Label(text=("Your IP is {}".format(socket.gethostbyname(socket.gethostname()))), bg="#00CCFF",
                     fg="white", height=1, width=20)

    ip_label.place(x=25, y=160)
    nick_name_label.place(x=20, y=10)
    status_label.place(x=25, y=180)
    port_label.place(x=25, y=40)
    entry_port.place(x=55, y=40)
    start_button.place(x=35, y=70)

    start_button.bind("<Button-1>", func=port_bind)


    window.mainloop()

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

A_t_A_button.bind("<Button-1>",func=A_t_a_mode)
S_S_button.bind("<Button-1>",func=server_sync)
A_S_button.bind("<Button-1>",func=all_sync)

root.mainloop()
