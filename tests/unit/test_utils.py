import asyncio

import pytest

from brainslug.utils import SyncedVar


@pytest.mark.asyncio
async def test_syncedvar_get_is_a_coroutine(event_loop):
    class Foo:
        bar = SyncedVar()

    foo = Foo()
    coro = foo.bar

    assert asyncio.iscoroutine(coro)

    asyncio.create_task(coro).cancel()


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_syncedvar_get_hangs(event_loop):
    class Foo:
        bar = SyncedVar()

    foo = Foo()

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(foo.bar, 1)


@pytest.mark.asyncio
async def test_syncedvar_get_finish_if_set_is_called(event_loop):
    class Foo:
        bar = SyncedVar()

    foo = Foo()
    sentinel = object()

    get_task = asyncio.create_task(foo.bar)
    foo.bar = sentinel

    assert await get_task is sentinel


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_syncedvar_second_time_get_also_hangs(event_loop):
    class Foo:
        bar = SyncedVar()

    foo = Foo()
    sentinel = object()

    get_task = asyncio.create_task(foo.bar)
    foo.bar = sentinel
    await get_task

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(foo.bar, 1)
