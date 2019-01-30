RIBOSOMES = dict()


class Symbol(tuple):
    def __getattribute__(self, name):
        if name.isidentifier():
            return Symbol(self + (name, ))
        else:
            raise AttributeError('Invalid attribute %r' % name)
