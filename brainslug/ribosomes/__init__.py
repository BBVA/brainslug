__all__ = ['define', 'ribosome', 'Remote']


RIBOSOMES = dict()  #: Global ribosome registry


class Symbol(tuple):
    def __getattr__(self, name):
        if name.isidentifier():
            return Symbol(self + (name, ))
        else:
            raise AttributeError('Invalid attribute %r' % name)


ribosome = Symbol()  #: Base ribosome


def define(symbol):
    def _register(fn):
        def is_dunder(s):
            return s.startswith("__") and s.endswith("__")

        if any(is_dunder(part) for part in symbol):
            raise ValueError("Cannot define double underscore methods")
        elif symbol in RIBOSOMES:
            raise ValueError("Cannot define ribosome twice")
        else:
            return RIBOSOMES.setdefault(symbol, fn)

    return _register


class Remote:
    def __init__(self, symbol, channel=None, root=None):
        self.__symbol__ = symbol
        self.__channel__ = channel
        self.__root__ = self if root is None else root

    def __getattr__(self, name):
        if name.isidentifier():
            return Remote(self.__symbol__ + (name, ), root=self.__root__)
        else:
            raise AttributeError('Invalid attribute %r' % name)

    def __call__(self, *args, **kwargs):
        return RIBOSOMES[self.__symbol__](self.__root__, *args, **kwargs)

    def __getitem__(self, name):
        return RIBOSOMES[self.__symbol__ + ('getitem', )](self.__root__, name)

    def __setitem__(self, name, value):
        return RIBOSOMES[self.__symbol__+('setitem',)](self.__root__,
                                                       name, value)

    def __delitem__(self, name):
        return RIBOSOMES[self.__symbol__ + ('delitem', )](self.__root__, name)
