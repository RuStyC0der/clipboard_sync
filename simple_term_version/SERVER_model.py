# coding=utf-8
import socket
import pickle
import pyperclip
import threading
from time import sleep


class Server():

    work_mode = None

    clients = {}

    client_clip = None
    clip_user = None
    request = None
    request_user = None

    controller_work_flag = False

    # Create server with socket obl.
    def __init__(self, port=9090, ip="", listen=1):
        self.sock = socket.socket()
        self.sock.bind((ip, port))
        self.sock.listen(listen)

        self.clip = None

    def add_client(self, timeout=0.01, client_timeout=0.1):
        self.sock.settimeout(timeout)  # wait timeout to connect user

        try:
            conn, addr = self.sock.accept()
        except:
            return
        name = pickle.loads(conn.recv(1024))
        print(name, " connected")
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
            except socket.timeout:  # WARNING:  This work only when timeouts activated in add_client func
                return False
            except EOFError:
                return False
            except pickle.UnpicklingError:
                print("recive part only") # For debugging)
                continue
        return data

    def _recive_server_controller(self):
        for i in self.clients:
            data = self._reciv_core(self.clients[i])
            if not data:
                continue
            if data[-1] == "clip":
                print("recived clip", i)
                self.client_clip = data[0]
                self.clip_user = i
            elif data[-1] == "request":
                print("recived_request", i)
                self.request = data[0]
                self.request_user = i

    def update(self, timeout=0.1):
            self.add_client()
            self._recive_server_controller()
            sleep(timeout)


class All_sync(Server):

    work_mode = "all_sync"

    def update(self, timeout=0.1):
            super().update(timeout)
            clip = self.get_clip()
            if clip != self.clip:
                for i in self.clients:
                    self.clients[i].send(pickle.dumps((self.clip, "clip")))
                self.clip = clip
            if self.client_clip:

                self.clip = self.client_clip
                self.set_clip(self.client_clip)
                for i in self.clients.keys().remove(self.clip_user):
                    self.clients[i].send(pickle.dumps((self.clip, "clip")))
                self.client_clip = False



if __name__ == '__main__':
#     name = input("| Name>>>")
#     # addres = input("| ip>>>")
#     port = int(input("| Port>>>"))
#     obj = All_sync(nickname=name, port=port)
    port = 9090
    obj = All_sync(port=port)
    while True:
        obj.update(0.1)