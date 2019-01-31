import asyncio
import gc
import pytest
import warnings

from aiohttp import web


@pytest.fixture
def cli(aiohttp_client, loop):
    from brainslug.web import config_routes
    app = web.Application()
    config_routes(app)
    return loop.run_until_complete(aiohttp_client(app))


@pytest.yield_fixture()
def event_loop():
    oldloop = asyncio.get_event_loop()
    wfilters = warnings.filters.copy()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        warnings.filterwarnings("ignore")
        yield loop
    finally:
        loop.close()
        gc.collect()
        warnings.filters = wfilters  # Restore old filters
        asyncio.set_event_loop(oldloop)
