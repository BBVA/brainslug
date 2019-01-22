import asyncio
import inspect

from tinydb import TinyDB, Query
import pytest

from brainslug import ChannelStorage


def testis_a_class():
    assert inspect.isclass(ChannelStorage)


def test_has_a_tinydb_database():
    cs = ChannelStorage()
    assert isinstance(cs._db, TinyDB)


@pytest.mark.asyncio
async def test_search_return_content():
    cs = ChannelStorage()
    expected = {}
    await cs.insert(expected)
    [current] = cs.search(Query())
    assert current == expected


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_wait_for_new_channel_hangs(event_loop):
    cs = ChannelStorage()
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(cs.wait_for_new_channel(), timeout=1)


@pytest.mark.asyncio
async def test_wait_for_new_channel_wakes_on_insert(event_loop):
    cs = ChannelStorage()
    task = asyncio.create_task(cs.wait_for_new_channel())
    await asyncio.sleep(0)  # Give a chance to wait to adquire the lock
    await cs.insert({})
    await asyncio.wait_for(task, 1)  # SHOULD NOT RAISE
