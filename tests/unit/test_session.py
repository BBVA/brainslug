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
async def test_first_step_hangs_without_the_other_side(event_loop, session):
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(session.first_step(), 1)


@pytest.mark.asyncio
async def test_first_step_returns_code_after_remote_eval(event_loop, session):
    code = object()

    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(session.remote_eval(code), 1)

    assert await session.first_step() is code
