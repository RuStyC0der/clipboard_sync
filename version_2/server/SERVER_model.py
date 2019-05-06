# coding=utf-8
import socket
import pickle
import pyperclip
import threading
from time import sleep

class _Singleton: # All subclaes of this class is a singletones
    __obj = False  # Private class variable.

    def __new__(cls,*args, **kwargs):
        if cls.__obj:
            # print('get instane')
            return cls.__obj
        # print('New')
        cls.__obj = super(_Singleton, cls).__new__(cls)
        return cls.__obj


class _Fake_sock_obj(_Singleton):
    def __init__(self, send,recive):
        self.send = send
        self.recv = recive

class Server():

    work_mode = None

    clients = {}


    client_clip = None
    clip_user = None
    request = None
    request_user = None

    controller_work_flag = False

    def __init__(self, nickname, ip="", port=9090, listen=1): # Create server with socket obl.
        self.sock = socket.socket()
        self.sock.bind((ip, port))
        self.sock.listen(listen)

        self.nickname = nickname

        self.clients[nickname] = _Fake_sock_obj(self.fake_send, self.fake_recive)

        self.clip = None
        self.old_clip = pyperclip.paste()

    def add_client(self, timeout=1, client_timeout=0.1): # wait timeout to connect user
        self.sock.settimeout(timeout)

        try:
            conn, addr = self.sock.accept()
        except:
            return
        name = pickle.loads(conn.recv(1024))
        # conn.send(pickle.dumps(self.work_mode))
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
        for i in self.clients:
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
                self._recive_server_controller()
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


    def fake_send(self,obj):
        if pickle.loads(obj)[-1] == "request":
            self.clip = self.get_clip()
            self.clip_user = self.nickname
        elif pickle.loads(obj)[-1] == "clip":
            self.set_clip(pickle.loads(obj)[0])

    def fake_recive(self,size):
        raise socket.timeout




class Server_sync(Server):

    work_mode = "server_sync"

    def start(self, timeout):
        super().start(timeout)
        def rec():
            while self.controller_work_flag:
                self.clip = self.get_clip()
                if self.old_clip != self.clip:
                    for i in self.clients:
                        self.clients[i].send(pickle.dumps((self.clip, "clip")))
                    self.old_clip = self.clip
        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()


class All_sync(Server):

    work_mode = "all_sync"


    def start(self, timeout):
        super().start(timeout)
        def rec():
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
        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()


class All_to_All(Server):

    work_mode = "all_to_all"

    def get_usr_clip(self, name):
        self.clients[name].send(("clip", "request"))

        while not self.client_clip: sleep(0.1)

        if self.clip_user == self.request:
            self.set_clip(self.client_clip)
            client_clip, clip_user, request, request_user = None


    def start(self, timeout):
        super().start(timeout)
        def rec():
            while self.controller_work_flag:
                if self.request:
                    if self.request == "user_list":
                        self.clients[self.request_user].send(pickle.dumps((self.clients.values(), "user_list")))
                    else:
                        self.clients[self.request].send(pickle.dumps(("clip", "request")))

                        while not self.client_clip: sleep(0.1)

                        if self.clip_user == self.request:
                            self.clients[self.request_user].send(pickle.dumps((self.client_clip, "clip")))
                            client_clip, clip_user, request, request_user = None
        thread = threading.Thread(target=rec)
        thread.daemon = True
        thread.start()
if __name__ == '__main__':
    a = All_to_All("miller")
    a.start(0.1)
    print("start")
    sleep(2)
    a.stop()
    print("StopIteration")
    a.destroy()
    print("destroy")
