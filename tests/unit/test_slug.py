import asyncio
import inspect
import threading
from unittest.mock import MagicMock as Mock
from unittest.mock import patch

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


def test_slug_contains_the_event_loop():
    slug = Slug(None, None)
    assert slug.loop is asyncio.get_event_loop()


def test_slug_create_is_a_decorator_returning_a_slug():
    @Slug.create()
    def foo():
        pass

    assert isinstance(foo, Slug)


def test_slug_create_respect_parameters():
    spec = object()
    def fn():
        pass

    slug = Slug.create(spec=spec)(fn)

    assert slug.fn is fn
    assert slug.spec == {'spec': spec}


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
    slug = Slug(None, None)
    await slug.run_in_thread(fn)
    fn.assert_called_once()


@pytest.mark.asyncio
async def test_run_in_thread_returns_same_as_fn(event_loop):
    expected = object()
    def fn():
        return expected
    slug = Slug(None, None)
    assert await slug.run_in_thread(fn) is expected


@pytest.mark.asyncio
async def test_run_in_thread_raise_fn_exception(event_loop):
    class CustomException(Exception):
        pass

    def fn():
        raise CustomException()

    slug = Slug(None, None)
    with pytest.raises(CustomException):
        await slug.run_in_thread(fn)


@pytest.mark.asyncio
async def test_run_in_thread_calls_function_in_a_thread(event_loop):
    slug = Slug(None, None)
    this_thread = threading.currentThread()
    other_thread = await slug.run_in_thread(threading.currentThread)
    assert this_thread != other_thread


@pytest.mark.asyncio
async def test_attach_resources_waits_for_resources(event_loop):
    slug = Slug(lambda:None, None)
    async def _wait_for_resources():
        return {}
    with patch('brainslug.utils.wait_for_resources') as wait_for_resources:
        wait_for_resources.return_value = _wait_for_resources()
        await slug.attach_resources()
        wait_for_resources.assert_called_once()


@pytest.mark.asyncio
async def test_attach_resources_return_fn_wrapped(event_loop):
    resources = object()
    called = False
    def fn(arg):
        nonlocal called
        assert arg is resources
        called = True
    async def _wait_for_resources():
        return {'arg': resources}
    slug = Slug(fn, None)
    with patch('brainslug.utils.wait_for_resources') as wait_for_resources:
        wait_for_resources.return_value = _wait_for_resources()
        wrapped = await slug.attach_resources()
        wrapped()
        assert called


@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_runs_the_slug_in_a_thread_with_resources(event_loop):
    from brainslug import ChannelStorage, Brain
    resource = object()
    called = None

    class Language:
        def __new__(cls, *args, **kwargs):
            return resource

    @Slug.create(res=Brain.foo == 'bar')
    def fn(res):
        nonlocal called
        called = True
        assert res is resource
        return threading.currentThread()

    with patch('brainslug.CHANNELS', ChannelStorage()) as CHANNELS:
        await CHANNELS.insert({'__language__': Language,
                               '__channel__': None,
                               'foo': 'bar'})
        thread_id = await fn.run()

        assert called
        assert thread_id is not None
        assert thread_id is not threading.currentThread()
