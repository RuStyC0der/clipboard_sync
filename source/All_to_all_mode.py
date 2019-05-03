from time import sleep
import socket
import pickle
import pyperclip
import threading

sock = socket.socket()
sock.bind(('', 9000))
sock.listen(10)
print("Server started")

user_list = {}

clip = None
clip_user = None
clip_ch_flag = None

request = None
request_user = None
request_ch_flag = None

work_mode = None


def add_user(work_mode, timeout=1):
    global user_list
    sock.settimeout(timeout)
    try:
        conn, addr = sock.accept()
    except:
        return
    name = pickle.loads(conn.recv(1024))
    conn.send(pickle.dumps(work_mode))
    print(name)
    print(conn)
    print(addr)
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


t1 = threading.Thread(target=server_get_clip)
t1.daemon = True
ff = True
add_user("all_to_all", 100)
while True:
    add_user("all_to_all")
    recive_server_controller()
    all_to_all_send_recv()
    if ff:
        t1.start()
        ff = False