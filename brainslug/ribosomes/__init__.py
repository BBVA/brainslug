RIBOSOMES = dict()


def define(symbol):
    def _decorated(fn):
        if symbol in RIBOSOMES:
            raise ValueError("Cannot define ribosome twice")
        else:
            RIBOSOMES[symbol] = fn
            return fn
    return _decorated


class Symbol(tuple):
    def __getattribute__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattribute__(name)
        elif name.isidentifier():
            return Symbol(self + (name, ))
        else:
            raise AttributeError('Invalid attribute %r' % name)
