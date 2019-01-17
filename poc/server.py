

class _RemoteException(Exception):
    __instances__ = dict()

    def __getattr__(self, name):
        if name not in self.__instances__:
            self.__instances__[name] = type(f"RemoteException.{name}",
                                            (self.__class__, ),
                                            {})
        return self.__instances__[name]


RemoteException = _RemoteException()


class Registrable(type):
    def __new__(

class Remote:

    exception = RemoteException

    def __init__(self, id):
        self.id = id

    def __getattr__(self, name):
        if 

