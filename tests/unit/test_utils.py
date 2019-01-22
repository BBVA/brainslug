from unittest.mock import MagicMock as Mock
from unittest.mock import patch
import threading

import pytest
from hypothesis import given
from hypothesis import strategies as st

from brainslug.utils import to_remote, get_resources
from brainslug import ChannelStorage, Brain


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
async def test_get_resources_calls_store_search_for_each_spec(keys, event_loop):
    store = Mock()
    spec = {k: Brain[k] == k for k in keys}
    get_resources(event_loop, store, spec)
    assert store.search.call_count == len(keys)


@given(keys=st.sets(st.text()))
@pytest.mark.asyncio
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
