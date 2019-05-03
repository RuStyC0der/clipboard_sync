# coding=utf-8
import pickle
d = "sfdt123124345hry\nerhrum"
print(d)
bytd = pickle.dumps(d)
print(bytd)
new = pickle.loads(bytd)
print(new)
y = b'\x80\x03X\x17\x00\x00\x00sfdt123124345hry\nerhrumq\x00.'
print(type(y))
z = pickle.loads(y)
print(z)