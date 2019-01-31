from brainslug import ribosome


class Remote:
    def __init__(self, symbol, eval=None, root=None):
        self.__symbol__ = symbol
        self.__eval__ = eval
        self.__root__ = self if root is None else root

    @classmethod
    def from_agent_info(cls, loop, agent_info):
        root = ribosome.root(agent_info['__ribosome__'])
        channel = agent_info['__channel__']

        def _run_threadsafe(code):
            return asyncio.run_coroutine_threadsafe(
                channel.remote_eval(code), loop).result()

        return cls(root, _run_threadsafe)

    def __getattr__(self, name):
        if name.isidentifier():
            return Remote(self.__symbol__ + (name, ), root=self.__root__)
        else:
            raise AttributeError('Invalid attribute %r' % name)

    def __call__(self, *args, **kwargs):
        return ribosome.RIBOSOMES[self.__symbol__](self.__root__, *args, **kwargs)

    def __getitem__(self, name):
        return ribosome.RIBOSOMES[self.__symbol__ + ('getitem', )](self.__root__, name)

    def __setitem__(self, name, value):
        return ribosome.RIBOSOMES[self.__symbol__+('setitem',)](self.__root__,
                                                       name, value)

    def __delitem__(self, name):
        return ribosome.RIBOSOMES[self.__symbol__ + ('delitem', )](self.__root__, name)
