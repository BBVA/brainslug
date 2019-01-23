from brainslug import webapp
import asyncio
import aiohttp
import pytest


def test_config_routes_is_a_function():
    assert callable(webapp.config_routes), "config routes must be a function"


def test_config_routes_return_the_same_app():
    origin = aiohttp.web.Application()
    assert webapp.config_routes(origin) is origin, "config routes must return the same app"


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
