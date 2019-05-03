# coding=utf-8
# this is socket client
import socket
import pyperclip
import pickle
from time import sleep
sock = socket.socket()
ip = "192.168.0.45"
sock.connect((ip, 9090))
print("connected to ip",ip)

def all_sync():
    old_clipboard = pyperclip.paste()
    ch_flag = False
    while True:
        client_clipboard = pyperclip.paste()
        sock.send(pickle.dumps((client_clipboard, ch_flag)))
        server_clipboard, ch_flag_server = pickle.loads(sock.recv(4096))
        if old_clipboard != client_clipboard:
            ch_flag = True
            old_clipboard = client_clipboard
            print("clipboard has been changed (client)")
        else:
            ch_flag = False
        if ch_flag_server is True and server_clipboard != client_clipboard:
            client_clipboard = server_clipboard
            print("clipboard has been changed (server)")
        pyperclip.copy(client_clipboard)
        sleep(0.5)
all_sync()
sock.close()