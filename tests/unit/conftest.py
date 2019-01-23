import warnings
import pytest
import asyncio

from aiohttp import web


@pytest.fixture
def cli(aiohttp_client):
    from brainslug.webapp import process_agent_request
    app = web.Application()
    app.router.add_post('/channel/{lang}/{id}', process_agent_request)
    return asyncio.get_event_loop().run_until_complete(aiohttp_client(app))


@pytest.yield_fixture()
def event_loop_nowarn():
    warnings.filterwarnings("ignore")
    try:
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()
    finally:
        warnings.resetwarnings()
