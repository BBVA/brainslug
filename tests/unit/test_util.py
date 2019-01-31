from unittest.mock import MagicMock as Mock
from unittest.mock import patch
import itertools
import asyncio
import threading

from hypothesis import given
from hypothesis import strategies as st
import pytest

from brainslug.database import AsyncTinyDB
from brainslug import body
from brainslug.runtime import get_resources
from brainslug.runtime import wait_for_resources
from brainslug.remote import Remote


@pytest.mark.asyncio
async def test_from_agent_info_builds_a_safe_lambda(event_loop):
    code = object()
    result = object()
    future = Mock()
    future.result.return_value = result

    with patch('asyncio.run_coroutine_threadsafe', return_value=future) as rct:
        channel = Mock()
        doc = {'__ribosome__': lambda x: [x], '__channel__': channel}

        # Language is instantiated with the lambda 
        remote = Remote.from_agent_info(event_loop, doc)

        assert remote.__eval__(code) is result  # We call the generated lambda
        channel.remote_eval.assert_called_once_with(code)
        rct.assert_called_once_with(channel.remote_eval(code), event_loop)


@pytest.mark.asyncio
async def test_get_resources_success_on_no_query(event_loop):
    assert get_resources(event_loop, AsyncTinyDB(), {}) == {}


@pytest.mark.asyncio
async def test_get_resources_returns_none_when_spec_not_satisfied(event_loop):
    store = AsyncTinyDB()
    spec = {'foo': body.foo == 'bar'}
    assert get_resources(event_loop, store, spec) is None


@given(keys=st.sets(st.text()))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_get_resources_calls_store_search_for_each_spec(keys, event_loop):
    store = Mock()
    spec = {k: body[k] == k for k in keys}
    get_resources(event_loop, store, spec)
    assert store.search.call_count == len(keys)


@given(keys=st.sets(st.text()))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_get_resources_calls_from_agent_info_for_each_doc_found(keys, event_loop):
    store = AsyncTinyDB()
    for key in keys:
        await store.insert({key: key})

    spec = {k: body[k] == k for k in keys}
    with patch('brainslug.remote.Remote.from_agent_info') as from_agent_info:
        get_resources(event_loop, store, spec)
        assert from_agent_info.call_count == len(keys)


@given(keys=st.sets(st.text()))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_get_resources_calls_from_agent_info_and_returns_in_dict_value(keys, event_loop):
    store = AsyncTinyDB()
    for key in keys:
        await store.insert({key: key})

    spec = {k: body[k] == k for k in keys}

    def _from_agent_info(loop, doc):
        for k in doc:
            return k

    with patch('brainslug.remote.Remote.from_agent_info', _from_agent_info) as from_agent_info:
        resources = get_resources(event_loop, store, spec)
        assert resources == {k: k for k in keys}


async def test_wait_for_resources_return_resources(event_loop):
    resources = object()
    with patch('brainslug.runtime.get_resources') as get_resources:
        get_resources.return_value = resources

        assert await wait_for_resources(event_loop, None, None) is resources


@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_wait_for_resources_hangs_if_no_resources(event_loop):
    class store:
        wait_for_insert = staticmethod(lambda: asyncio.sleep(0))
    spec = {'foo': body['foo'] == 'bar'}

    with patch('brainslug.runtime.get_resources') as get_resources:
        get_resources.side_effect = itertools.repeat(None)

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(wait_for_resources(event_loop, store, spec), 1)

        get_resources.assert_called()


@given(num_fails=st.integers(min_value=0, max_value=100))
@pytest.mark.asyncio
@pytest.mark.slowtest
async def test_wait_for_resources_calls_wait_for_every_failed_get_resources(event_loop, num_fails):
    store = Mock()
    store.wait_for_insert.side_effect = lambda: asyncio.sleep(0)
    spec = {'foo': body['foo'] == 'bar'}
    result = {'foo': object()}
    with patch('brainslug.runtime.get_resources') as get_resources:
        get_resources.side_effect = itertools.chain(
            itertools.repeat(None, num_fails),
            [result])

        await asyncio.wait_for(wait_for_resources(event_loop, store, spec), 1)

        assert get_resources.call_count == num_fails + 1
        assert store.wait_for_insert.call_count == num_fails
