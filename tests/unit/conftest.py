import warnings
import pytest
import asyncio

from aiohttp import web


@pytest.fixture
def cli(aiohttp_client, loop):
    from brainslug.webapp import config_routes
    app = web.Application()
    config_routes(app)
    return loop.run_until_complete(aiohttp_client(app))


@pytest.yield_fixture()
def event_loop_nowarn():
    warnings.filterwarnings("ignore")
    try:
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()
    finally:
        warnings.resetwarnings()
