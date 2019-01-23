"""
Contains the application runtime primitives and the global state.

"""
from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools
import weakref

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

from brainslug import utils

#: Used to query for resources
Brain = Query()


class ChannelStorage:
    """
    A tiny wrapper over TinyDB to allow notifications on insert.

    """
    def __init__(self):
        self._db = TinyDB(storage=MemoryStorage)
        self._new_channel = asyncio.Condition()

    async def wait_for_new_channel(self):
        async with self._new_channel:
            await self._new_channel.wait()

    async def insert(self, *args, **kwargs):
        ret = self._db.insert(*args, **kwargs)
        async with self._new_channel:
            self._new_channel.notify_all()
        return ret

    def search(self, *args, **kwargs):
        return self._db.search(*args, **kwargs)


# Global application state
CHANNELS = ChannelStorage()


class Channel:
    """
    Manage the communication channel between an agent and one or more
    remote instances.

    """
    _code = utils.SyncedVar()
    _result = utils.SyncedVar()

    def __init__(self):
        self._eval_lock = asyncio.Lock()

    async def remote_eval(self, code):
        """
        Arrange the execution of `code` on the remote agent, eventually
        returning its result.

        """
        async with self._eval_lock:
            self._code = code
            return await self._result

    async def first_step(self):
        """Return the first code to be evaluated by the remote agent."""
        return await self._code

    async def next_step(self, last_result):
        """
        Receive the result of the last evaluation and return the next
        code to evaluate eventually.

        """
        self._result = last_result
        return await self._code


class Slug:
    def __init__(self, fn, spec):
        self.fn = fn
        self.spec = spec
        self.loop = asyncio.get_event_loop()

    @classmethod
    def create(cls, **spec):
        return functools.partial(Slug, spec=spec)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    async def run_in_thread(self, fn):
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await self.loop.run_in_executor(executor, fn)

    async def attach_resources(self):
        resources = await utils.wait_for_resources(self.loop,
                                                   CHANNELS,
                                                   self.spec)
        return functools.partial(self.fn, **resources)

    async def run(self):
        prepared = await self.attach_resources()
        return await self.run_in_thread(prepared)


run_web_server = None
