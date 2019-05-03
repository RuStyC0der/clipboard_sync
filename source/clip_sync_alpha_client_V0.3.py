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
print("workmode is", "all sync" if work_mode == 1 else ("server sync" if work_mode == 2 else "all-to-all access"))

old_clip = pyperclip.paste()

user_list = {nickname, "server"}
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

def get_myclip():
    global old_clip
    clip = pyperclip.paste()
    if old_clip != clip:
        old_clip = clip
        return clip, True
    else:
        return clip, False

def all_sync():
    global clip_ch_flag, clip
    my_clip, ch_flag = get_myclip()
    if ch_flag and my_clip != clip:
        sock.send(pickle.dumps([my_clip, "clip"]))
    else:
        if clip_ch_flag:
            clip_ch_flag = False
            pyperclip.copy(clip)

def server_sync():
    global clip_ch_flag, clip
    if clip_ch_flag:
        clip_ch_flag = False
        pyperclip.copy(clip)


def all_to_all_send_recv_client():
    global clip, clip_ch_flag, user_list, request, request_ch_flag
    if request_ch_flag:
        request_ch_flag = False
        sock.send(pickle.dumps([pyperclip.paste(),"clip"]))

def get_clip_client():
    global clip, clip_ch_flag, user_list, request, request_ch_flag, user_list_ch_flag
    while True:
        name = input("get name, input list to view user list")
        if name == 'list':
            sock.send(pickle.dumps(["user_list_get", "request"]))
            while not user_list_ch_flag: pass
            user_list_ch_flag = False
            print(user_list)
            continue
        if name not in user_list:
            continue
        sock.send(pickle.dumps([name, "request"]))
        while True:
            if clip_ch_flag:
                clip_ch_flag = False
                pyperclip.copy(clip)
                print("clip pasted to clip", name)
                break

t1 = threading.Thread(target=get_clip_client)
t1.daemon = True
ff = True
while True:
    client_revive_controller()
    if work_mode == 1:
        all_sync()
    elif work_mode == 2:
        server_sync()
    else :
        all_to_all_send_recv_client()
        if ff:
            t1.start()
            ff = False
    sleep(1)