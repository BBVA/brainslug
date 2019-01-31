import asyncio

from tinydb import TinyDB
from tinydb.storages import MemoryStorage


class AsyncTinyDB:
    """
    A tiny wrapper over TinyDB to allow notifications on insert.

    """
    def __init__(self):
        self._db = TinyDB(storage=MemoryStorage)
        self._new_channel = asyncio.Condition()

    async def wait_for_insert(self):
        async with self._new_channel:
            await self._new_channel.wait()

    async def insert(self, *args, **kwargs):
        ret = self._db.insert(*args, **kwargs)
        async with self._new_channel:
            self._new_channel.notify_all()
        return ret

    def search(self, *args, **kwargs):
        return self._db.search(*args, **kwargs)
