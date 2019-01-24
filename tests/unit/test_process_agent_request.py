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
        await process_agent_request(language, key, meta, None)
        [res] = CHANNELS.search((Q['__key__'] == key)
                                & (Q['__language__'] == language)
                                & (Q[meta_key] == meta_value))
        assert isinstance(res['__channel__'], Channel)


# TODO: next_step if channel exists
# TODO: first_step if channel not exists
# TODO: check next_code when channel exists
# TODO: check next_code when channel not exists
