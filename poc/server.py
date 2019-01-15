

class _RemoteException(Exception):
    __instances__ = dict()

    def __getattr__(self, name):
        if name not in self.__instances__:
            self.__instances__[name] = type(f"RemoteException.{name}",
                                            (self.__class__, ),
                                            {})
        return self.__instances__[name]


RemoteException = _RemoteException()


class _RemoteVar:
    def __init__(self, id, type):
        self.id = id
        self.type = type

    def __str__(self):
        """Return the code to fetch the variable remotely."""
        raise NotImplementedError()

class RemoteFileHandler(_RemoteVar):
    def __init__( # XXX



class Task:

    exception = RemoteException

    def __init__(self, id):
        self.id = id

