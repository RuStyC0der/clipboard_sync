# coding=utf-8
import socket
import pickle
import pyperclip
import threading
from time import sleep

class Singleton: # All subclaes of this class is singletones
    __obj = False  # Private class variable.

    def __new__(cls,*args, **kwargs):
        if cls.__obj:
            # print('get instane')
            return cls.__obj
        # print('New')
        cls.__obj = super(Singleton, cls).__new__(cls)
        return cls.__obj

class Server(Singleton):

    clients = {}


    client_clip = None
    clip_user = None
    request = None
    request_user = None

    controller_work_flag = False

    def __init__(self, ip="", port=9090, listen=1): # Create server with socket obl.
        self.sock = socket.socket()
        self.sock.bind((ip, port))
        self.sock.listen(listen)

        self.clip = None
        self.old_clip = pyperclip.paste()

    def add_client(self, timeout=1, client_timeout=0.1): # wait timeout to connect user
        self.sock.settimeout(timeout)

        try:
            conn, addr = self.sock.accept()
        except:
            return
        name = pickle.loads(conn.recv(1024))
        conn.settimeout(client_timeout)
        self.clients[name] = conn
        return (name, addr)

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
                # print("recive part only") # For debugging)
                continue
        return data

    def _recive_server_controller(self):
        for i in self.user_list:
            data = self._reciv_core(self.clients[i])
            if not data:
                continue
            if data[-1] == "clip":
                # print("recived clip", i)
                self.client_clip = data[0]
                self.clip_user = i
            elif data[-1] == "request":
                # print("recived_request", i)
                self.request = data[0]
                self.request_user = i

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


class Server_sync(Server):
    def start(self, timeout):
        super().start(timeout)
        while self.controller_work_flag:
            self.clip = self.get_clip()
            if self.old_clip != self.clip:
                for i in self.clients:
                    self.clients[i].send(pickle.dumps((self.clip, "clip")))
                self.old_clip = self.clip



class All_sync(Server):
        def start(self, timeout):
            super().start(timeout)
            while self.controller_work_flag:
                self.clip = self.get_clip()
                if self.old_clip != self.clip:
                    for i in self.clients:
                        self.clients[i].send(pickle.dumps((self.clip, "clip")))
                    self.old_clip = self.clip
                if self.client_clip:
                    self.old_clip = self.client_clip
                    self.clip = self.client_clip
                    self.set_clip(self.client_clip)
                    for i in self.clients.keys().remove(self.clip_user):
                        self.clients[i].send(pickle.dumps((self.clip, "clip")))



class All_to_All(Server):
        def start(self, timeout):
            super().start(timeout)
            while self.controller_work_flag:
                pass
