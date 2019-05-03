# coding=utf-8
import socket
import pickle
from time import sleep
# BlockingIOError

ip = ""
port = 9091

sock = socket.socket()
sock.bind((ip,port))




sock.listen(10)


conn, addr = sock.accept()
print(addr, "connected")
conn.setblocking(0)


joined_data = b''
while True:
    try:
        data = conn.recv(4096)
        print(11)
        joined_data += data
        data = pickle.loads(joined_data)
        break
    except BlockingIOError :
        print("bad")
        break
    except pickle.UnpicklingError:
        print("continue")
        continue


print(data)
print(len(data))
