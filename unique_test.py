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
    pass

a = Server()
a = Server()
del(a)
a = Server()
