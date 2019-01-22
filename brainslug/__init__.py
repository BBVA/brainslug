"""
Contains the application runtime primitives and the global state.

"""
import asyncio
import functools
import weakref

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from brainslug.utils import SyncedVar


# Global application state
CHANNELS = TinyDB(storage=MemoryStorage)


class Channel:
    """
    Manage the communication channel between an agent and one or more
    remote instances.

    """
    _code = SyncedVar()
    _result = SyncedVar()

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

    @classmethod
    def create(cls, spec=None):
        return functools.partial(Slug, spec=spec)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)
