import pytest
import asyncio
from unittest.mock import patch

from tinydb import Query

from brainslug.webapp import process_agent_request
from brainslug.channel import ChannelStorage, Channel


def test_process_agent_request_is_a_function():
    assert callable(process_agent_request), "process_agent_request must be a function"


@pytest.mark.asyncio
async def test_channel_is_created_if_not_exists():
    language = object()
    key = object()
    meta_key = object()
    meta_value = object()
    meta = {
        meta_key: meta_value
    }
    Q = Query()
    with patch('brainslug.channel.CHANNELS', new=ChannelStorage()) as CHANNELS:
        with patch('brainslug.channel.Channel.first_step') as first_step:
            first_step.return_value = asyncio.sleep(0)
            await process_agent_request(language, key, meta, None)
            [res] = CHANNELS.search((Q['__key__'] == key)
                                    & (Q['__language__'] == language)
                                    & (Q[meta_key] == meta_value))
            assert isinstance(res['__channel__'], Channel)


@pytest.mark.asyncio
async def test_channel_call_first_step_if_not_exists(event_loop):
    with patch('brainslug.channel.CHANNELS', new=ChannelStorage()):
        with patch('brainslug.channel.Channel.first_step') as first_step:
            first_step.return_value = asyncio.sleep(0)
            await process_agent_request(None, None, {}, None)
            first_step.assert_called_once()


# TODO: next_step if channel exists
# TODO: check next_code when channel exists
# TODO: check next_code when channel not exists
