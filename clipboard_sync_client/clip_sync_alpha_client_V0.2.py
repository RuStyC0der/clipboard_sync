# coding=utf-8
# this is socket client
import socket
import pyperclip
import pickle
import threading
from time import sleep
sock = socket.socket()
ip = "192.168.0.45"
nickname = input("Enter yor nickname: ")
sock.connect((ip, 9000))
sock.send(pickle.dumps(nickname))
print("connected to ip",ip)
work_mode = pickle.loads(sock.recv(1024))
print("workmode is", work_mode)

old_clip = pyperclip.paste()
names = [nickname,"Server"]
clip = None

def get_clip(conn):
    conn.settimeout(1)
    try:
        data = conn.recv(4096)
    except: return False
    client_clip = pickle.loads(data)
    return client_clip
def send_clip(clip, conn):
    conn.send(pickle.dumps(clip))
def get_myclip():
    global old_clip
    clip = pyperclip.paste()
    if old_clip != clip:
        old_clip = clip
        return clip, True
    else:
        return clip, False

def all_sync():
    clip, ch_flag = get_myclip()
    if ch_flag:
        send_clip(clip, sock)
    else:
        pyperclip.copy(get_clip(sock))
def server_sync(sock):
    while True:
        data = sock.recv(4096)
        if data != b'':
            break
    pyperclip.copy(pickle.loads(data))

def all_to_all_send():
    global clip
    global names
    while True:
        while True:
            data = sock.recv(4096)
            if data != b'':
                break
        data = pickle.loads(data)
        if data:
            sock.send(pickle.dumps(pyperclip.paste()))
            continue
        data = pickle.loads(data)
        if type(data) == list:
            names = data
            print(names)
        else:
            clip = data

def all_to_all_recv():
    global names
    while True:
        sock.send(pickle.dumps("get_users_list"))
        print("request sended...")
        name = input("get name: ")
        if name == "names_list":
            print(names)
        if name not in [i for i in names]:
            return
        sock.send(pickle.dumps(name))
        sleep(0.1)
        print("clip recived")
        pyperclip.copy(pickle.loads(clip))

t1 = threading.Thread(target=all_to_all_send)

t2 = threading.Thread(target=all_to_all_recv)
t1.daemon = True
t2.daemon = True

ff = True
while True:
    if ff:
        print("t1 started")
        t1.start()
    if ff:
        t2.start()
        print("t2 started")
        ff = False

    sleep(1)