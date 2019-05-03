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
            print('get instane')
            return cls.__obj
        print('New')
        cls.__obj = super(Singleton, cls).__new__(cls)
        return cls.__obj

class Server(Singleton):

    clients = {}
    clip = None
    old_clip = pyperclip.paste
    client_clip = None
    request = None
    request_user = None

    def __init__(self, ip="", port=9090, listen=1): # Create server with socket obl.
        self.sock = socket.socket()
        self.sock.bind((ip, port))
        self.sock.listen(listen)
        self.clip = pyperclip.paste()

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
            except socket.timeout: # This work only when timeouts activated in add_client func
                return False
            except EOFError:
                return False
            except pickle.UnpicklingError:
                # print("recive part only") # For debugging)
                continue
        return data



class All_sync(Server):
    pass




