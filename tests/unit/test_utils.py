from unittest.mock import MagicMock as Mock
import threading

import pytest

from brainslug.utils import run_in_thread


@pytest.mark.asyncio
async def test_run_in_thread_calls_function(event_loop):
    fn = Mock()
    await run_in_thread(fn)
    fn.assert_called_once()


@pytest.mark.asyncio
async def test_run_in_thread_returns_same_as_fn(event_loop):
    expected = object()
    def fn():
        return expected
    assert await run_in_thread(fn) is expected


@pytest.mark.asyncio
async def test_run_in_thread_raise_fn_exception(event_loop):
    class CustomException(Exception):
        pass

    def fn():
        raise CustomException()

    with pytest.raises(CustomException):
        await run_in_thread(fn)


@pytest.mark.asyncio
async def test_run_in_thread_calls_function_in_a_thread(event_loop):
    this_thread = threading.currentThread()
    other_thread = await run_in_thread(threading.currentThread)
    assert this_thread != other_thread
