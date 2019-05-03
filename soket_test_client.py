# coding=utf-8
# this is socket client
import socket
sock = socket.socket()

import pickle
d = True
print()

sock.connect(("127.0.0.1", 9000))
sock.send(b'\x80\x03X\x17\x00\x00\x00sfdt123124345hry\nerhrumq\x00.')
sock.close()