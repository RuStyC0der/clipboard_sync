from time import sleep
import socket
import pickle
sock = socket.socket()

sock.bind(('',9000))
sock.listen(5)

