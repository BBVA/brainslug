RIBOSOMES = dict()


class Symbol(tuple):
    def __getattribute__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattribute__(name)
        elif name.isidentifier():
            return Symbol(self + (name, ))
        else:
            raise AttributeError('Invalid attribute %r' % name)
