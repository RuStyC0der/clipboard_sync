from time import sleep
import socket
import pickle
import pyperclip

sock = socket.socket()
sock.bind(('',9090))
sock.listen(10)
print("Server started")
conn, addr = sock.accept()
print("Client connected in addres",addr)

def all_sync(conn):
    old_clip = pyperclip.paste()
    ch_flag = False
    data = b''
    while True:
        while True:
            data = conn.recv(4096)
            if data != b'':
                break
        server_clip = pyperclip.paste()
        client_clip, ch_flag_client = pickle.loads(data)
        conn.send(pickle.dumps((server_clip,ch_flag)))
        if old_clip != server_clip:
            ch_flag = True
            old_clip = server_clip
            print("clipboard has been changed (server)")
        else:
            ch_flag = False
        if ch_flag_client == True:
            server_clip = client_clip
            print("clipboard has been changed (client)")

        pyperclip.copy(server_clip)
        sleep(0.5)


all_sync(conn)