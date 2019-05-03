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

    def __init__(self, ip, nickname,port=9090):
        self.sock = socket.socket()
        self.sock.connect((ip, port))
        self.sock.send(pickle.dumps(nickname))
        self.sock.settimeout(0.1)
        self.clip = pyperclip.paste()
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
