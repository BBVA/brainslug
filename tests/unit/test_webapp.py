from brainslug import webapp
import asyncio
import aiohttp
import pytest
import unittest


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
    webapp.config_routes(app)
    cli = await aiohttp_client(app)
    resp = await cli.post('/channel/powershell/pepe')
    assert resp.status == 200, "channel endpoint must respond"


async def test_channel_must_call_par(aiohttp_client, loop):
    app = aiohttp.web.Application()
    with unittest.mock.patch('brainslug.webapp.process_agent_request') as par_mock:
        par_mock.return_value = asyncio.sleep(0)
        webapp.config_routes(app)
        cli = await aiohttp_client(app)
        resp = await cli.post('/channel/powershell/pepe')
        assert resp.status == 200, "channel endpoint must respond"
        par_mock.assert_called_once()


async def test_channel_must_call_par_with_correct_arguments(aiohttp_client, loop):
    app = aiohttp.web.Application()
    with unittest.mock.patch('brainslug.webapp.process_agent_request') as par_mock:
        par_mock.return_value = asyncio.sleep(0)
        webapp.config_routes(app)
        cli = await aiohttp_client(app)
        resp = await cli.post('/channel/powershell/pepe')
        assert resp.status == 200, "channel endpoint must respond"
        par_mock.assert_called_once()
        par_mock.assert_called_once_with("powershell", "pepe", None, None)
