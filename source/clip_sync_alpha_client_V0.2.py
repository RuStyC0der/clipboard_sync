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
sock.connect((ip, 9090))
sock.send(pickle.dumps(nickname))
print("connected to ip",ip)
work_mode = pickle.loads(sock.recv(1024))
print("workmode is", work_mode)

old_clip = pyperclip.paste()
clients = [nickname,"Server"]

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
    while True:
        data = sock.recv(4096)
        if data != b'':
            break
    if data == b'\x80\x03\x88.':
        sock.send(pickle.dumps(pyperclip.paste()))

def all_to_all_recv():
    sock.send(pickle.dumps("get_users_list"))
    names = sock.recv(4096)
    name = input("get name: ")
    if name not in [i for i in names]:
        return
    name.send(b'\x80\x03\x88.')
    clip = sock.recv(4096)
    pyperclip.copy(pickle.loads(clip))

t1 = threading.Thread(target=all_to_all_send())
t2 = threading.Thread(target=all_to_all_recv())

while True:
    if not t1.is_alive():

        t1.start()
    if not t2.is_alive():
        t2.start()


