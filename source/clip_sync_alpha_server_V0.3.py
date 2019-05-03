import socket
import pickle
import pyperclip
import threading
from time import sleep

sock = socket.socket()
sock.bind(('', 9000))
sock.listen(10)
print("Server started")

work_mode = None

user_list = {}
old_clip = pyperclip.paste()

clip = None
clip_user = None
clip_ch_flag = None

request = None
request_user = None
request_ch_flag = None


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


def server_sync():
    global user_list
    sock.settimeout(None)
    server_clip, ch_flag = get_myclip()
    if ch_flag:
        print("clip changed to server clip")
        for j in user_list:
            user_list[j][0].send(pickle.dumps([server_clip, "clip"]))


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


def server_get_clip():
    global clip, clip_ch_flag, user_list, request, request_ch_flag, clip_user, request_user
    while True:
        name = input("get name, input list to view user list")
        if name == 'list':
            print([i for i in user_list])
            continue
        if name not in [i for i in user_list]:
            continue
        user_list[name][0].send(pickle.dumps(["get_clip", "request"]))
        while True:
            if clip_ch_flag:
                clip_ch_flag = False
                pyperclip.copy(clip)
                print("clip pasted to clip", name)
                break
            sleep(0.1)


while work_mode not in range(1, 4):
    work_mode = int(input("Enter work mode:\n 1 - Full sync\n 2 - Server sync \n 3 - All to All access\n>>>"))

t1 = threading.Thread(target=server_get_clip)
t1.daemon = True
ff = True
add_user(work_mode, 100)
while True:
    add_user(work_mode)
    recive_server_controller()
    if work_mode == 1:
        all_sync()
    elif work_mode == 2:
        server_sync()
    else:
        all_to_all_send_recv()
        if ff:
            t1.start()
            ff = False
