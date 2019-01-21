from contextlib import suppress
import asyncio
import pytest

from brainslug import Channel


def test_channel_needs_no_parameters():
    Channel()  # SHOULD NOT RAISE


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_step_hangs_without_the_other_side(event_loop):
    channel = Channel()
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(channel.first_step(), 1)


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_step_returns_code_after_remote_eval(event_loop):
    channel = Channel()
    code = object()

    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(channel.remote_eval(code), 1)

    assert await channel.first_step() is code


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_remote_eval_hangs_without_the_other_side(event_loop):
    channel = Channel()
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(channel.remote_eval(None), 1)


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_remote_eval_hangs_after_first_step(event_loop):
    channel = Channel()
    task = asyncio.create_task(channel.first_step())
    try:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(channel.remote_eval(None), 1)
    finally:
        task.cancel()


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_remote_eval_returns_first_next_step_data(event_loop):
    channel = Channel()
    result = object()

    task = asyncio.create_task(channel.remote_eval(None))
    await channel.first_step()
    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(channel.next_step(result), 1)

    assert await task is result


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_next_step_hangs_after_first_remote_eval(event_loop):
    channel = Channel()
    task = asyncio.create_task(channel.remote_eval(None))
    await channel.first_step()

    try:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(channel.next_step(None), 1)
    finally:
        task.cancel()


@pytest.mark.asyncio
async def test_first_next_step_returns_second_remote_eval_code(event_loop):
    channel = Channel()
    code = object()

    async def right_side():
        await channel.first_step()
        return await channel.next_step(None)

    async def left_side():
        await channel.remote_eval(None)
        await channel.remote_eval(code)

    task_right = asyncio.create_task(right_side())
    task_left = asyncio.create_task(left_side())

    try:
        assert await task_right is code
    finally:
        task_left.cancel()


@pytest.mark.asyncio
async def test_second_remote_eval_returns_second_next_step_result(event_loop):
    channel = Channel()
    result = object()

    async def right_side():
        await channel.first_step()
        await channel.next_step(None)
        await channel.next_step(result)

    async def left_side():
        await channel.remote_eval(None)
        return await channel.remote_eval(None)

    task_right = asyncio.create_task(right_side())
    task_left = asyncio.create_task(left_side())

    try:
        assert await task_left is result
    finally:
        task_right.cancel()


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_remote_eval_cant_be_used_in_parallel(event_loop):
    channel = Channel()

    async def right_side():
        await channel.first_step()
        await channel.next_step(None)

    async def left_side():
        await channel.remote_eval(None)

    task_left1 = asyncio.create_task(left_side())
    task_left2 = asyncio.create_task(left_side())
    task_right = asyncio.create_task(right_side())

    # One of the left tasks should finish
    done, pending = await asyncio.wait([task_left1, task_left2],
                                       return_when=asyncio.FIRST_COMPLETED)

    assert len(done) == len(pending) == 1

    pending = pending.pop()

    # The other should hang
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(pending, timeout=1)

    task_right.cancel()
    pending.cancel()
