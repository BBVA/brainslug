from unittest.mock import patch
import asyncio

from hypothesis import given
from hypothesis import strategies as st
import aiohttp
import pytest

from brainslug import web


def test_config_routes_is_a_function():
    assert callable(web.config_routes), "config routes must be a function"


def test_config_routes_return_none():
    origin = aiohttp.web.Application()
    assert web.config_routes(origin) is None, "config routes must return none"


async def test_channel_not_found_without_parameters(aiohttp_client, cli):
    resp = await cli.post('/channel', data={})
    assert resp.status == 404, "must return not found if no parameters"


async def test_channel_must_respond(aiohttp_client, loop, cli):
    current_langs = {
        "powershell": "powershell_lang"
    }

    with patch('brainslug.web.process_agent_request') as process_agent_request:
        with patch.dict('brainslug.ribosome.RIBOSOMES', current_langs):
            process_agent_request.return_value = asyncio.sleep(0)
            resp = await cli.post('/channel/powershell/pepe')
            assert resp.status == 200, "channel endpoint must respond"


async def test_channel_must_call_par(aiohttp_client, loop, cli):
    current_langs = {
        "powershell": "powershell_lang"
    }

    with patch('brainslug.web.process_agent_request') as process_agent_request:
        with patch.dict('brainslug.ribosome.RIBOSOMES', current_langs):
            process_agent_request.return_value = asyncio.sleep(0)
            resp = await cli.post('/channel/powershell/pepe')
            assert resp.status == 200, "channel endpoint must respond"
            process_agent_request.assert_called_once()


async def test_channel_must_call_par_with_correct_arguments(aiohttp_client, loop, cli):
    with patch('brainslug.web.process_agent_request') as process_agent_request:
        process_agent_request.return_value = asyncio.sleep(0)
        resp = await cli.post('/channel/powershell/pepe')
        assert resp.status == 200, "channel endpoint must respond"
        process_agent_request.assert_called_once_with("powershell", "pepe", {}, b'')


async def test_channel_input_must_retrieve_custom_metadata(aiohttp_client, loop, cli):
    current_langs = {
        "powershell": "powershell_lang"
    }

    with patch('brainslug.web.process_agent_request') as process_agent_request:
        with patch.dict('brainslug.languages.RIBOSOMES', current_langs):
            process_agent_request.return_value = asyncio.sleep(0)
            resp = await cli.post('/channel/powershell/pepe?custom=true')
            assert resp.status == 200, "response must be Ok"
            process_agent_request.assert_called_once_with("powershell_lang", "pepe", {"custom":"true"}, b'')


@given(payload=st.binary())
def test_channel_input_must_receive_last_result(aiohttp_client, loop, cli, payload):
    async def _test():
        with patch('brainslug.web.process_agent_request') as process_agent_request:
            process_agent_request.return_value = asyncio.sleep(0)
            resp = await cli.post('/channel/powershell/pepe', data=payload)
            assert resp.status == 200, "response must be Ok"
            process_agent_request.assert_called_once_with("powershell", "pepe", {}, payload)
    loop.run_until_complete(_test())


async def test_channel_input_must_retrieve_custom_metadata(aiohttp_client, loop, cli):
    current_langs = {
        "powershell": "powershell_lang"
    }

    result = object()
    async def _process_agent_request():
        return str(id(result)).encode('ascii')

    with patch('brainslug.web.process_agent_request') as process_agent_request:
        with patch.dict('brainslug.ribosome.RIBOSOMES', current_langs):
            process_agent_request.return_value = _process_agent_request()
            resp = await cli.post('/channel/powershell/pepe')
            assert await resp.read() == str(id(result)).encode('ascii')
