from contextlib import suppress
import asyncio
import pytest

from brainslug import Session


def test_session_needs_some_parameters():
    with pytest.raises(TypeError):
        Session()


def test_session_store_attributes():
    agent_type = object()
    machine_id = object()
    process_id = object()

    session = Session(agent_type, machine_id, process_id)

    assert session.agent_type is agent_type
    assert session.machine_id is machine_id
    assert session.process_id is process_id


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_step_hangs_without_the_other_side(event_loop, session):
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(session.first_step(), 1)


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_step_returns_code_after_remote_eval(event_loop, session):
    code = object()

    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(session.remote_eval(code), 1)

    assert await session.first_step() is code


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_remote_eval_hangs_without_the_other_side(event_loop, session):
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(session.remote_eval(None), 1)


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_remote_eval_hangs_after_first_step(event_loop, session):

    task = asyncio.create_task(session.first_step())
    try:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(session.remote_eval(None), 1)
    finally:
        task.cancel()


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_first_remote_eval_returns_first_next_step_data(event_loop, session):
    result = object()

    task = asyncio.create_task(session.remote_eval(None))
    await session.first_step()
    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(session.next_step(result), 1)

    assert await task is result


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_next_step_hangs_after_first_remote_eval(event_loop, session):
    task = asyncio.create_task(session.remote_eval(None))
    await session.first_step()

    try:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(session.next_step(None), 1)
    finally:
        task.cancel()


@pytest.mark.asyncio
async def test_first_next_step_returns_second_remote_eval_code(event_loop, session):
    code = object()

    async def right_side():
        await session.first_step()
        return await session.next_step(None)

    async def left_side():
        await session.remote_eval(None)
        await session.remote_eval(code)

    task_right = asyncio.create_task(right_side())
    task_left = asyncio.create_task(left_side())

    try:
        assert await task_right is code
    finally:
        task_left.cancel()


@pytest.mark.asyncio
async def test_second_remote_eval_returns_second_next_step_result(event_loop, session):
    result = object()

    async def right_side():
        await session.first_step()
        await session.next_step(None)
        await session.next_step(result)

    async def left_side():
        await session.remote_eval(None)
        return await session.remote_eval(None)

    task_right = asyncio.create_task(right_side())
    task_left = asyncio.create_task(left_side())

    try:
        assert await task_left is result
    finally:
        task_right.cancel()
