RIBOSOMES = dict()


def define(symbol):
    def _decorated(fn):
        def is_dunder(s):
            return s.startswith("__") and s.endswith("__")
        if any(is_dunder(part) for part in symbol):
            raise ValueError("Cannot define double underscore methods")
        elif symbol in RIBOSOMES:
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
