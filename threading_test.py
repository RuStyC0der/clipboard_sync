from time import sleep
import threading
z = 10
def updigit():
    global z
    while True:
        z += 1
        print(z)
        sleep(1)
def changer():
    global z
    while True:
        z = int(input(">>>"))

t1 = threading.Thread(target=updigit)
t2 = threading.Thread(target=changer)
t1.daemon = True
t2.daemon = True
while True:
    print(t1.isAlive())
    if not (t1.is_alive()):
        print("starting thread 1....")
        t1.start()
    if not (t2.is_alive()):
        print("starting thread 2....")
        t2.start()