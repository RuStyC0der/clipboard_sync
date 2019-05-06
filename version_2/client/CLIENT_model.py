# coding=utf-8
# from sys import exit
from time import sleep
import socket
import pickle
import pyperclip
import threading

class Singleton: # All subclaes of this class is singletones
    __obj = False  # Private class variable.

    def __new__(cls,*args, **kwargs):
        if cls.__obj:
            print('get instane')
            return cls.__obj
        print('New')
        cls.__obj = super(Singleton, cls).__new__(cls)
        return cls.__obj

class Client(Singleton):

    user_list = None

    recived_clip = None

    request = None

    controller_work_flag = False



    def __init__(self,nickname, ip, port=9090):
        self.sock = socket.socket()
        self.sock.connect((ip, port))
        self.sock.send(pickle.dumps(nickname))
        self.sock.settimeout(0.1)

        self.clip = None
        self.old_clip = pyperclip.paste()

        self.nickname = nickname

    def get_clip(self):
        return pyperclip.paste()

    def set_clip(self, clip):
        pyperclip.copy(clip)

    @staticmethod
    def _reciv_core(conn):
        joined_data = b''
        while True:
            try:
                data = conn.recv(4096)
                joined_data += data
                data = pickle.loads(joined_data)
                break
            except socket.timeout: # WARNING:  This work only when timeouts activated in add_client func
                return False
            except EOFError:
                return False
            except pickle.UnpicklingError:
                # print("recived part") # DEBUG print
                continue
        return data

    def _recive_client_controller(self):
        data = self._reciv_core(self.sock)
        if not data:
            return
        if data[-1] == "clip":
            self.recived_clip = data[0]
        elif data[-1] == "request":
            self.request = data[0]
        else:
            self.user_list = data[0]

    def start(self, timeout=0.1):
        self.controller_work_flag = True
        self.timeout = timeout
        def rec():
            while self.controller_work_flag:
                self.recive_server_controller()
                sleep(self.timeout)

        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()

        def stop(self):
            self.controller_work_flag = False

        def destroy(self):
            self.controller_work_flag = False
            sleep(0.1)
            self.sock.close()
            self.sock.shutdown(socket.SHUT_RDWR)
            self.__del__()

class Server_sync():
    def start(self, timeout):
        super().start(timeout)
        def rec():
            while self.controller_work_flag:
                if self.recived_clip:
                    self.set_clip(self.recived_clip)
                    self.recived_clip = False
        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()

class All_sync(Client):
    def start(self, timeout):
        super().start(timeout)
        def rec():
            while self.controller_work_flag:
                self.clip = self.get_clip()
                if self.clip != self.old_clip:
                    self.old_clip = self.clip
                    self.sock.send(pickle.dumps((self.clip, "clip")))
                if self.recived_clip:
                    self.set_clip(self.recived_clip)
                    self.old_clip = self.recived_clip
                    self.clip = self.recived_clip
                    self.recived_clip = False

        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()

class All_to_All(Client):

    def refresh_user_list(self):
        self.sock.send(pickle.dumps((True, "user_list")))

    def get_usr_clip(self, name):
        self.clients[name].send(("clip", "request"))


    def start(self, timeout):
        super().start(timeout)
        def rec():
            while self.controller_work_flag:
                if self.request:
                    if self.request == "clip":
                        self.sock.send(pickle.dumps((self.get_clip(), "clip")))
                if self.recived_clip:
                    self.set_clip(self.recived_clip)
                    self.recived_clip = False

        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()
