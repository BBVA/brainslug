from unittest.mock import MagicMock as Mock
from unittest.mock import patch
import itertools
import asyncio
import threading

from hypothesis import given
from hypothesis import strategies as st
import pytest

from brainslug import ChannelStorage, Brain
from brainslug.utils import get_resources
from brainslug.utils import to_remote
from brainslug.utils import wait_for_resources


@pytest.mark.asyncio
async def test_to_remote_builds_a_safe_lambda(event_loop):
    code = object()
    result = object()
    future = Mock()
    future.result.return_value = result

    with patch('asyncio.run_coroutine_threadsafe', return_value=future) as rct:
        channel = Mock()
        doc = {'__language__': lambda x: [x], '__channel__': channel}

        # Language is instantiated with the lambda 
        [_run_threadsafe] = to_remote(event_loop, doc)

        assert _run_threadsafe(code) is result  # We call the generated lambda
        channel.remote_eval.assert_called_once_with(code)
        rct.assert_called_once_with(channel.remote_eval(code), event_loop)


@pytest.mark.asyncio
async def test_get_resources_success_on_no_query(event_loop):
    assert get_resources(event_loop, ChannelStorage(), {}) == {}


@pytest.mark.asyncio
async def test_get_resources_returns_none_when_spec_not_satisfied(event_loop):
    store = ChannelStorage()
    spec = {'foo': Brain.foo == 'bar'}
    assert get_resources(event_loop, store, spec) is None


@given(keys=st.sets(st.text()))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_get_resources_calls_store_search_for_each_spec(keys, event_loop):
    store = Mock()
    spec = {k: Brain[k] == k for k in keys}
    get_resources(event_loop, store, spec)
    assert store.search.call_count == len(keys)


@given(keys=st.sets(st.text()))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_get_resources_calls_to_remote_for_each_doc_found(keys, event_loop):
    store = ChannelStorage()
    for key in keys:
        await store.insert({key: key})

    spec = {k: Brain[k] == k for k in keys}
    with patch('brainslug.utils.to_remote') as to_remote:
        get_resources(event_loop, store, spec)
        assert to_remote.call_count == len(keys)


@given(keys=st.sets(st.text()))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_get_resources_calls_to_remote_and_returns_in_dict_value(keys, event_loop):
    store = ChannelStorage()
    for key in keys:
        await store.insert({key: key})

    spec = {k: Brain[k] == k for k in keys}

    def _to_remote(loop, doc):
        for k in doc:
            return k

    with patch('brainslug.utils.to_remote', _to_remote) as to_remote:
        resources = get_resources(event_loop, store, spec)
        assert resources == {k: k for k in keys}


async def test_wait_for_resources_return_resources(event_loop):
    resources = object()
    with patch('brainslug.utils.get_resources') as get_resources:
        get_resources.return_value = resources

        assert await wait_for_resources(event_loop, None, None) is resources


@pytest.mark.asyncio
async def test_wait_for_resources_hangs_if_no_resources(event_loop):
    class store:
        wait_for_new_channel = staticmethod(lambda: asyncio.sleep(0))
    spec = {'foo': Brain['foo'] == 'bar'}

    with patch('brainslug.utils.get_resources') as get_resources:
        get_resources.side_effect = itertools.repeat(None)

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(wait_for_resources(event_loop, store, spec), 1)

        get_resources.assert_called()


@given(num_fails=st.integers(min_value=0, max_value=100))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_wait_for_resources_calls_wait_for_every_failed_get_resources(event_loop, num_fails):
    store = Mock()
    store.wait_for_new_channel.side_effect = lambda: asyncio.sleep(0)
    spec = {'foo': Brain['foo'] == 'bar'}
    result = {'foo': object()}
    with patch('brainslug.utils.get_resources') as get_resources:
        get_resources.side_effect = itertools.chain(
            itertools.repeat(None, num_fails),
            [result])

        await asyncio.wait_for(wait_for_resources(event_loop, store, spec), 1)

        assert get_resources.call_count == num_fails + 1
        assert store.wait_for_new_channel.call_count == num_fails
