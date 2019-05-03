from time import sleep
import socket
import pickle
import pyperclip
import threading

sock = socket.socket()
sock.bind(('', 9000))
sock.listen(10)
print("Server started")


users = {}
old_clip = pyperclip.paste()
work_mode = None


def send_client_list(users):
    c_list = [i for i in users] + ["Server"]
    for i in users:
        users[i][0].send(pickle.dumps(c_list))


def add_user(work_mode, timeout=1):
    global users
    sock.settimeout(timeout)
    try:
        conn, addr = sock.accept()
    except:
        return
    name = pickle.loads(conn.recv(1024))
    conn.send(pickle.dumps(work_mode))
    users[name] = (conn, addr, name)
    print(name, "connected from ip", addr[0])


def get_clip(conn):
    conn.settimeout(1)
    try:
        data = conn.recv(4096)
    except:
        return False
    client_clip = pickle.loads(data)
    return client_clip


def send_clip(clip, conn):
    conn.send(pickle.dumps(clip))


def get_myclip():
    global old_clip
    server_clip = pyperclip.paste()
    if old_clip != server_clip:
        old_clip = server_clip
        return server_clip, True
    else:
        return server_clip, False


def all_sync():
    global users
    global old_clip
    sock.settimeout(None)
    server_clip, ch_flag = get_myclip()
    if ch_flag:
        print("clip changed to server clip")
        for j in users:
            send_clip(server_clip, users[j][0])
        return
    for i in users:
        tmp_clip = get_clip(users[i][0])
        if tmp_clip:
            print(i, "change clipboard")
            for j in users:
                send_clip(tmp_clip, users[j][0])
            pyperclip.copy(tmp_clip)
            old_clip = tmp_clip
            break


def server_sync():
    global users
    sock.settimeout(None)
    server_clip, ch_flag = get_myclip()
    if ch_flag:
        print("clip changed to server clip")
        for j in users:
            send_clip(server_clip, users[j][0])


def recive_send_all():
    while True:
        global users
        for i in users:
            users[i][0].setblocking(0)
            try:
                request = pickle.loads((users[i])[0].recv(4096))
            except:
                continue
            users[i][0].setblocking(1)
            print("reqest is: ", request)
            if request == "get_users_list":
                users[i][0].send(pickle.dumps([i for i in users] + ["Server"]))
                continue
            if request == "Server":
                (users[i])[0].send(pickle.dumps(pyperclip.paste()))
                continue
            (users[request])[0].send(b'\x80\x03\x88.')
            (users[i])[0].send((users[request])[0].recv(4096))


def server_get_all():
    while True:
        global users
        print("Names:", [i for i in users])
        name = input("get name: ")
        if name not in [i for i in users]:
            continue
        users[name][0].setblocking(1)
        users[name][0].send(b'\x80\x03\x88.')
        clip = users[name][0].recv(4096)
        pyperclip.copy(pickle.loads(clip))


t1 = threading.Thread(target=recive_send_all)
t2 = threading.Thread(target=server_get_all)
t2.daemon = True
t1.daemon = True

while work_mode not in range(1, 4):
    work_mode = int(input("Enter work mode:\n 1 - Full sync\n 2 - Server sync \n 3 - All to All access\n>>>"))

if work_mode == 1:
    work_mode = 'Full sync'
elif work_mode == 2:
    work_mode = 'Server sync'
else:
    work_mode = 'All to All access'
add_user(work_mode, 100)
ff = True
while True:
    add_user(work_mode)
    if work_mode == 'Full sync':
        all_sync()
    elif work_mode == 'Server sync':
        server_sync()
    else:
        if ff:
            t1.start()
            print("t1")
        if ff:
            t2.start()
            print("t2")
            ff = False
    sleep(1)
