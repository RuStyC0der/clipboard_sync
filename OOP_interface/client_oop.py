# coding=utf-8


# from sys import exit
from time import sleep
import socket
import pickle
# import pyperclip
import threading

class pyperclip():
    clip_file = open("clip", mode="w")
    clip_file.close()

    @staticmethod
    def copy(value):
        clip_file = open("clip", mode="w")
        clip_file.write(value)
        clip_file.close()

    @staticmethod
    def paste():
        clip_file = open("clip")
        clip = clip_file.read()
        return clip


class Core_client():
    timeout = 0

    sock = socket.socket()


    old_clip = pyperclip.paste()

    user_list = ()
    old_user_list = ()
    user_list_ch_flag = False

    clip = None
    clip_ch_flag = None

    request = None
    request_ch_flag = None

    @classmethod
    def conect(cls,nickname, ip,port=9090):
        cls.sock.connect((ip,port))
        cls.sock.send(pickle.dumps(nickname))
        cls._work_mode = pickle.loads(cls.sock.recv(4096))
        cls.sock.settimeout(0.1)

    @classmethod
    def _get_myclip(cls):

        server_clip = pyperclip.paste()
        if cls.old_clip != server_clip:
            cls.old_clip = server_clip
            return server_clip, True
        else:
            return server_clip, False

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
                print("continue")
                continue
        return data

    @classmethod
    def client_revive_controller(cls):
        data = cls._reciv_core(cls.sock)
        if not data:
            return
        if data[-1] == "clip":
            print("recived clip")
            cls.clip = data[0]
            cls.clip_ch_flag = True
        elif data[-1] == "request":
            print("recived request")
            cls.request = data[0]
            cls.request_ch_flag = True
        else:
            print("recived user list")
            cls.user_list = data[0]
            cls.user_list_ch_flag = True


    @classmethod
    def start_controller(cls, timeout):
        sleep(timeout)
        def rec():
            while True:
                cls.client_revive_controller()
                sleep(cls.timeout)

        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()


class All_to_all_client(Core_client):  
    @classmethod
    def all_to_all_send_clip_client(cls):
        if cls.request_ch_flag:
            cls.request_ch_flag = False
            cls.sock.send(pickle.dumps([pyperclip.paste(), "clip"]))

    @classmethod
    def get_clip_client(cls, name):
        cls.sock.send(pickle.dumps([name, "request"]))
        while True:
            if cls.clip_ch_flag:
                cls.clip_ch_flag = False
                pyperclip.copy(cls.clip)
                print("clip pasted to clip", name)
                break

    @classmethod
    def refresh_user_list(cls):
        cls.sock.send(pickle.dumps(["user_list_get", "request"]))

    @classmethod
    def start_controller(cls, timeout):
        sleep(timeout)
        def rec():
            while True:
                cls.client_revive_controller()
                cls.all_to_all_send_clip_client()
                # cls.refresh_user_list()
                sleep(cls.timeout)

        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()

class All_sync_client(Core_client):

    @classmethod
    def all_sync(cls):
        my_clip, ch_flag = cls._get_myclip()
        if ch_flag and my_clip != cls.clip:
            cls.sock.send(pickle.dumps([my_clip, "clip"]))
        else:
            if cls.clip_ch_flag:
                cls.clip_ch_flag = False
                pyperclip.copy(cls.clip)

class Server_sync_client(Core_client):

    @classmethod
    def server_sync(cls):
        if cls.clip_ch_flag:
            cls.clip_ch_flag = False
            pyperclip.copy(cls.clip)


All_sync_client.conect("TEST", "192.168.0.101",port=9090)
print("connected")
# while True: # All_sync mode test
#     All_sync_client.client_revive_controller()
#     All_sync_client.all_sync()

All_to_all_client.start_controller(0.1)

while True:
    All_to_all_client.refresh_user_list()
    print(All_to_all_client.user_list)
    name = input(">>>")
    All_to_all_client.get_clip_client(name)
