import asyncio

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

    def __ribosome__(self, *parts):
        return ribosome.RIBOSOMES[self.__symbol__ + parts]

    def __call__(self, *args, **kwargs):
        return self.__ribosome__()(self.__root__, *args, **kwargs)

    def __getitem__(self, name):
        return self.__ribosome__('getitem')(self.__root__, name)

    def __setitem__(self, name, value):
        return self.__ribosome__('setitem')(self.__root__, name, value)

    def __delitem__(self, name):
        return self.__ribosome__('delitem')(self.__root__, name)
