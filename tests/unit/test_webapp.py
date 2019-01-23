from brainslug import webapp
import asyncio
import aiohttp
import pytest
from unittest.mock import patch


def test_config_routes_is_a_function():
    assert callable(webapp.config_routes), "config routes must be a function"


def test_config_routes_return_none():
    origin = aiohttp.web.Application()
    assert webapp.config_routes(origin) is None, "config routes must return none"


async def test_channel_not_found_without_parameters(aiohttp_client, loop):
    app = aiohttp.web.Application()
    webapp.config_routes(app)
    cli = await aiohttp_client(app)
    resp = await cli.post('/channel', data={})
    assert resp.status == 404, "must return not found if no parameters"


async def test_channel_must_respond(aiohttp_client, loop):
    app = aiohttp.web.Application()
    current_langs = {
        "powershell": "powershell_lang"
    }
    with patch.dict('brainslug.languages.LANGUAGES', current_langs):
        webapp.config_routes(app)
        cli = await aiohttp_client(app)
        resp = await cli.post('/channel/powershell/pepe')
        assert resp.status == 200, "channel endpoint must respond"


async def test_channel_must_call_par(aiohttp_client, loop):
    app = aiohttp.web.Application()
    current_langs = {
        "powershell": "powershell_lang"
    }

    with patch('brainslug.webapp.process_agent_request') as par_mock:
        with patch.dict('brainslug.languages.LANGUAGES', current_langs):
            par_mock.return_value = asyncio.sleep(0)
            webapp.config_routes(app)
            cli = await aiohttp_client(app)
            resp = await cli.post('/channel/powershell/pepe')
            assert resp.status == 200, "channel endpoint must respond"
            par_mock.assert_called_once()


async def test_channel_must_call_par_with_correct_arguments(aiohttp_client, loop):
    app = aiohttp.web.Application()
    current_langs = {
        "powershell": "powershell_lang"
    }

    with patch('brainslug.webapp.process_agent_request') as par_mock:
        with patch.dict('brainslug.languages.LANGUAGES', current_langs):
            par_mock.return_value = asyncio.sleep(0)
            webapp.config_routes(app)
            cli = await aiohttp_client(app)
            resp = await cli.post('/channel/powershell/pepe')
            assert resp.status == 200, "channel endpoint must respond"
            par_mock.assert_called_once()
            par_mock.assert_called_once_with("powershell_lang", "pepe", None, None)


async def test_channel_input_must_call_par_with_correct_language(aiohttp_client, loop):
    app = aiohttp.web.Application()
    with patch('brainslug.webapp.process_agent_request') as process_agent_request:
        with patch.dict('brainslug.LANGUAGES', {}):
            process_agent_request.return_value = asyncio.sleep(0)
            webapp.config_routes(app)
            cli = await aiohttp_client(app)
            resp = await cli.post('/channel/java/pepe')
            assert resp.status == 404, "language must not exists"
            process_agent_request.assert_not_called()

