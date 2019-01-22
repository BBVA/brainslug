import inspect
import threading
from unittest.mock import MagicMock as Mock

import pytest

from brainslug import Slug


def test_slug_is_a_class():
    assert inspect.isclass(Slug)


def test_slug_stores_attributes():
    fn = object()
    spec = object()
    slug = Slug(fn, spec)
    assert slug.fn is fn
    assert slug.spec is spec


def test_slug_create_is_a_decorator_returning_a_slug():
    @Slug.create()
    def foo():
        pass

    assert isinstance(foo, Slug)


def test_slug_create_respect_parameters():
    spec = object()
    def fn():
        pass

    slug = Slug.create(spec)(fn)

    assert slug.fn is fn
    assert slug.spec is spec


def test_slug_call_calls_fn():
    fn = Mock()
    slug = Slug(fn=fn, spec=None)
    slug()
    fn.assert_called_once()


def test_slug_is_a_passthrough_callable():
    expected_a = object()
    expected_b = object()
    expected_ret = object()

    def fn(current_a, current_b=None):
        assert current_a is expected_a
        return expected_ret

    slug = Slug(fn=fn, spec=None)

    assert slug(expected_a, current_b=expected_b) is expected_ret


@pytest.mark.asyncio
async def test_run_in_thread_calls_function(event_loop):
    fn = Mock()
    await Slug.run_in_thread(fn)
    fn.assert_called_once()


@pytest.mark.asyncio
async def test_run_in_thread_returns_same_as_fn(event_loop):
    expected = object()
    def fn():
        return expected
    assert await Slug.run_in_thread(fn) is expected


@pytest.mark.asyncio
async def test_run_in_thread_raise_fn_exception(event_loop):
    class CustomException(Exception):
        pass

    def fn():
        raise CustomException()

    with pytest.raises(CustomException):
        await Slug.run_in_thread(fn)


@pytest.mark.asyncio
async def test_run_in_thread_calls_function_in_a_thread(event_loop):
    this_thread = threading.currentThread()
    other_thread = await Slug.run_in_thread(threading.currentThread)
    assert this_thread != other_thread
