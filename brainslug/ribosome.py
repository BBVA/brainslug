from pkg_resources import iter_entry_points

RIBOSOMES = dict()  #: Global ribosome registry


class Symbol(tuple):
    def __getattr__(self, name):
        if name.isidentifier():
            return Symbol(self + (name, ))
        else:
            raise AttributeError('Invalid attribute %r' % name)


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


def root(name):
    return Symbol((name, ))


def load():
    for entrypoint in iter_entry_points('brainslug.ribosomes'):
        entrypoint.load()
