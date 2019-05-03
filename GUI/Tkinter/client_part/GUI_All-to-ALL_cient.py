from tkinter import *
from sys import exit
from time import sleep
import socket
import pickle
import pyperclip
import threading

sock = socket.socket()

old_clip = None

user_list = ()
old_user_list = ()
user_list_ch_flag = False

clip = None
clip_ch_flag = None

request = None
request_ch_flag = None


def client_revive_controller():
    global clip, clip_ch_flag, user_list, request, request_ch_flag, user_list_ch_flag
    sock.setblocking(0)
    try:
        data = pickle.loads(sock.recv(4096))
        print("data is:", data)
    except:
        return
    sock.setblocking(1)
    if data[-1] == "clip":
        print("recived clip")
        clip = data[0]
        clip_ch_flag = True
    elif data[-1] == "request":
        print("recived request")
        request = data[0]
        request_ch_flag = True
    else:
        print("recived user list")
        user_list = data[0]
        user_list_ch_flag = True


def GUI_all_to_all_mode():
    def all_to_all_send_recv_client():
        global clip, clip_ch_flag, user_list, request, request_ch_flag
        if request_ch_flag:
            request_ch_flag = False
            sock.send(pickle.dumps([pyperclip.paste(), "clip"]))

    def get_clip_client():
        global clip, clip_ch_flag, user_list, request, request_ch_flag, user_list_ch_flag
        while True:
            try:
                name = lbox.get(lbox.curselection())
            except:
                return
            sock.send(pickle.dumps([name, "request"]))
            while True:
                if clip_ch_flag:
                    clip_ch_flag = False
                    pyperclip.copy(clip)
                    print("clip pasted to clip", name)
                    break

    def refresh_user_list():
        global user_list_ch_flag, user_list, old_user_list
        sock.send(pickle.dumps(["user_list_get", "request"]))
        while not user_list_ch_flag: sleep(0.1)
        user_list_ch_flag = False
        for i in (set(user_list) - set(old_user_list)):
            lbox.insert(0, i)
        old_user_list = user_list

    def port_bind(event):
        port = entry_port.get()
        ip = ip_entry.get()
        nickname = nickname_entry.get()
        flag = False
        if not port.isdigit():
            entry_port.delete(0, END)
            entry_port.insert(0, "Incorrect port")
            entry_port.after(1000, lambda: entry_port.delete(0, END))
            flag = True
        if len(ip.split(".")) < 4:
            ip_entry.delete(0, END)
            ip_entry.insert(0, "Incorrect IP")
            ip_entry.after(1000, lambda: ip_entry.delete(0, END))
            flag = True
        if len(nickname) == 0:
            nickname_entry.delete(0, END)
            nickname_entry.insert(0, "Empty nickname")
            window.after(1000, lambda: nickname_entry.delete(0, END))
            flag = True
        if flag:
            return
        entry_port.destroy()
        ip_entry.destroy()
        nickname_entry.destroy()
        ip_value = Label(text=ip, bg="#33FFFF", fg="white")
        ip_value.place(x=55, y=20)
        nickname_value = Label(text=nickname, bg="#33FFFF", fg="white")
        nickname_value.place(x=55, y=60)
        port_label_value = Label(text=port, bg="#33FFFF", fg="white")
        port_label_value.place(x=55, y=40)
        start_button["text"] = "Exit"
        start_button.bind("<Button-1>", func=lambda x: exit())
        status_label["text"] = "Connecting..."
        status_label["bg"] = "green"
        sock.connect((ip, port))
        sock.send(pickle.dumps(nickname))
        work_thread.start()
        status_label["text"] = "Connected!"
        window.geometry("400x220")
        lbox.place(x=250, y=10)
        get_clip_button.place(x=250, y=180)
        refresh_button.place(x=340, y=180)
        get_clip_button.bind("<Button-1>", func=get_clip_client)
        refresh_button.bind("<Button-1>", func=refresh_user_list)

    def work_cycle():
        client_revive_controller()
        all_to_all_send_recv_client()
        sleep(0.1)

    work_thread = threading.Thread(target=work_cycle)
    work_thread.daemon = True

    window = Tk()
    window.resizable(False, False)
    window.geometry("200x220")
    window.title("A-t-A mode | Client")

    refresh_button = Button(window, text="R")
    get_clip_button = Button(window, text="Get Clipboard")
    lbox = Listbox(width=20, height=10)

    entry_port = Entry(width=15)
    port_label = Label(text="Port")

    ip_label = Label(text="IP")
    ip_entry = Entry(width=15)

    nickname_label = Label(text="Nick")
    nickname_entry = Entry(width=15)

    start_button = Button(window, text="Connect", width=17)
    status_label = Label(text="Not connected", bg="red", height=1, width=20)

    status_label.place(x=25, y=180)
    port_label.place(x=25, y=40)
    entry_port.place(x=55, y=40)
    ip_label.place(x=25, y=20)
    ip_entry.place(x=55, y=20)
    nickname_label.place(x=25, y=60)
    nickname_entry.place(x=55, y=60)
    start_button.place(x=30, y=90)

    start_button.bind("<Button-1>", func=port_bind)

    window.after(20000, lambda: window.destroy())
    window.mainloop()


GUI_all_to_all_mode()
