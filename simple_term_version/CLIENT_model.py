# coding=utf-8
import socket
import pickle
import pyperclip
import threading
from time import sleep


class Client():

    user_list = None

    recived_clip = None

    request = None

    controller_work_flag = False

    def __init__(self, nickname, ip, port=9090):
        self.sock = socket.socket()
        self.sock.settimeout(5)
        self.sock.connect((ip, port))
        self.sock.send(pickle.dumps(nickname))
        self.sock.settimeout(0.1)

        self.clip = None

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
            except socket.timeout:  # WARNING:  This work only when timeouts activated in add_client func
                return False
            except EOFError:
                return False
            except pickle.UnpicklingError:
                print("recived part")  # DEBUG print
                continue
        return data

    def _recive_client_controller(self):
        data = self._reciv_core(self.sock)
        if not data:
            return
        if data[-1] == "clip":
            print("recived clip")
            self.recived_clip = data[0]
        elif data[-1] == "request":
            print("recived reqest")
            self.request = data[0]
        else:
            self.user_list = data[0]

    def update(self, timeout=0.1):
        self._recive_client_controller()
        sleep(timeout)


class All_sync(Client):

    def update(self, timeout=0.1):
        super().update(timeout)
        clip = self.get_clip()
        if self.clip != clip:
            self.sock.send(pickle.dumps((self.clip, "clip")))
        if self.recived_clip:
            self.set_clip(self.recived_clip)
            self.clip = self.recived_clip
            self.recived_clip = False


if __name__ == '__main__':
    # name = input("| Name>>>")
    # addres = input("| ip>>>")
    # port = int(input("| Port>>>"))
    # obj = All_sync(nickname=name, port=port, ip=addres)
    name = "me"
    addres = ""
    port = 9090
    obj = All_sync(nickname=name, port=port, ip=addres)
    while True:
        obj.update()
