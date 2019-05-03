# coding=utf-8
# from sys import exit
import socket
import pickle
import pyperclip
import threading
from time import sleep


class Core_server():
    sock = socket.socket()

    user_list = {}

    work_mode = None


    clip = None
    old_clip = pyperclip.paste
    clip_user = None
    clip_ch_flag = None

    request = None
    request_user = None
    request_ch_flag = None

    def __init__(self, name, connect_obj, ip):
        self._name = name
        self._connect = connect_obj
        self._IP = ip

    @classmethod
    def start(cls, port, listen_queue=5, ip=""):
        cls.sock.bind((ip, int(port)))
        cls.sock.listen(listen_queue)

    @classmethod
    def _get_myclip(cls):

        server_clip = pyperclip.paste()
        if cls.old_clip != server_clip:
            cls.old_clip = server_clip
            return server_clip, True
        else:
            return server_clip, False

    @classmethod
    def add_user(cls, timeout=1):

        cls.sock.settimeout(timeout)
        try:
            conn, addr = cls.sock.accept()
        except:
            return
        name = pickle.loads(conn.recv(1024))
        conn.send(pickle.dumps(cls.work_mode))
        conn.settimeout(0.1)
        cls.user_list[name] = cls(name=name, connect_obj=conn, ip=addr)
        return (name, addr)

    @staticmethod
    def _reciv_core(conn):
        """

        :rtype: object self._
        """
        joined_data = b''
        while True:
            try:
                data = conn.recv(4096)
                joined_data += data
                data = pickle.loads(joined_data)
                break
            except socket.timeout:
                return False
            except EOFError:
                return False
            except pickle.UnpicklingError:
                # print("recived part") # For debugging)
                continue
        return data

    @classmethod
    def recive_server_controller(cls):
        for i in cls.user_list:
            data = cls._reciv_core(cls.user_list[i]._connect)
            if not data:
                continue
            if data[-1] == "clip":
                print("recived clip", i)
                cls.clip = data[0]
                cls.clip_ch_flag = True
                cls.clip_user = i
            elif data[-1] == "request":
                print("recived_request", i)
                cls.request = data[0]
                cls.request_user = i
                cls.request_ch_flag = True

    @classmethod
    def start_controller(cls,timeout):
        cls.timeout = timeout
        def rec():
            while True:
                cls.recive_server_controller()
                sleep(cls.timeout)

        thread = threading.Thread(target=rec())
        thread.daemon = True
        thread.start()

class All_to_all_mode_server(Core_server):

    work_mode = "All_to_All"

    @classmethod
    def all_to_all_send_recv(cls):
        if cls.request_ch_flag:
            cls.request_ch_flag = False
            if cls.request != "user_list_get":
                if cls.request == "server":
                    cls.user_list[cls.request_user]._connect.send(pickle.dumps([pyperclip.paste(), "clip"]))
                    return

                cls.user_list[cls.request]._connect.send(pickle.dumps(["get_clip", "request"]))
                while True:
                    if cls.clip_ch_flag:
                        cls.clip_ch_flag = False
                        cls.user_list[cls.request_user]._connect.send(pickle.dumps([cls.clip, "clip"]))
                        break
            else:
                cls.user_list[cls.request_user]._connect.send(pickle.dumps([[i for i in cls.user_list] + ["server"],
                                                                            "user_list"]))
                print("user list send")

    @classmethod
    def server_get_clip(cls, name):
        cls.user_list[name]._connect.send(pickle.dumps(["get_clip", "request"]))
        while True:
            if cls.clip_ch_flag:
                cls.clip_ch_flag = False
                pyperclip.copy(cls.clip)
                print("clip pasted to clip", name)
                break

    @classmethod
    def start_controller(cls,timeout):
        cls.timeout = timeout
        def rec():
            while True:
                cls.recive_server_controller()
                cls.all_to_all_send_recv()
                sleep(timeout)


        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()

class All_sync_server(Core_server):

    work_mode = "All_sync"

    @classmethod
    def all_sync(cls):
        server_clip, ch_flag = cls._get_myclip()
        if ch_flag:
            print("clip changed to server clip")
            for j in cls.user_list:
                cls.user_list[j]._connect.send(pickle.dumps([server_clip, "clip"]))
            return
        if cls.clip_ch_flag:
            cls.clip_ch_flag = False
            pyperclip.copy(cls.clip)
            cls.old_clip = cls.clip
            print("clip changing to ", cls.clip_user, " clip...")
            for j in [i for i in cls.user_list if i != cls.clip_user]:
                cls.user_list[j]._connect.send(pickle.dumps([cls.clip, "clip"]))
            print("done")

class Server_sync_server(Core_server):

    work_mode = "Server_sync"

    @classmethod
    def server_sync(cls):
        cls.sock.settimeout(None)
        server_clip, ch_flag = cls._get_myclip()
        if ch_flag:
            print("clip changed to server clip")
            for j in cls.user_list:
                cls.user_list[j]._connect.send(pickle.dumps([server_clip, "clip"]))

All_sync_server.start(9090)
print("started")
name, addr = All_sync_server.add_user(1000)
print("user", name , " connected in ip", addr)
# while True:
#     All_sync_server.recive_server_controller()
#     All_sync_server.all_sync()

All_to_all_mode_server.start_controller(0.1)
print("controller started")
while True:
    print(All_to_all_mode_server.user_list)
    name = input(">>>")
    All_to_all_mode_server.server_get_clip(name)