from functools import partial

LANGUAGES = RIBOSOMES = dict()


class Symbol(tuple):
    def __getattribute__(self, name):
        return Symbol(self + (name, ))

    def __call__(self, fn):
        if self in RIBOSOMES:
            raise RuntimeError("Cannot declare symbol twice.")
        else:
            return RIBOSOMES.setdefault(self, fn)


class Remote:
    def __init__(self, symbol, channel=None, root=None):
        self.__symbol__ = symbol
        self.__channel__ = channel
        self.__root__ = self if root is None else root

    def __ribosome__(self, *names):
        key = self.__symbol__ + tuple(names)
        try:
            return RIBOSOMES[key]
        except KeyError as exc:
            raise AttributeError(
                'Remote does not support %r' % '.'.join(key)) from exc

    def __getattribute__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return object.__getattribute__(self, name)
        else:
            symbol = self.__symbol__ + (name, )
            if symbol in RIBOSOMES:
                return partial(self.__ribosome__(name), self.__root__)
            else:
                return Remote(symbol, root=self.__root__)

    def __dir__(self):
        def startswith(prefix, it):
            return it[:len(prefix)] == prefix

        def _dir():
            this = self.__symbol__
            for symbol in RIBOSOMES.keys():
                if startswith(this, symbol):
                    yield '.'.join(symbol[len(this):len(this) + 1])

        return set(_dir())

    def __getitem__(self, name):
        return self.__ribosome__('__getitem__')(self.__root__, name)

    def __setitem__(self, name, value):
        return self.__ribosome__('__setitem__')(self.__root__, name, value)

    def __delitem__(self, name):
        return self.__ribosome__('__delitem__')(self.__root__, name)

    def __call__(self, *args, **kwargs):
        return self.__ribosome__()(self.__root__, *args, **kwargs)


ribosome = Symbol()  # Declare symbols with decorators
