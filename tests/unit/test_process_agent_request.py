import pytest
import asyncio
from aiohttp import web

# --- objects --------------------------------------------- #
def test_process_agent_request_exists():
    try:
        from brainslug.webapp import process_agent_request
    except ImportError as exc:
        assert False, exc


def test_process_agent_request_is_a_function():
    from brainslug.webapp import process_agent_request
    assert callable(process_agent_request), "process_agent_request must be a function"
# --- objects --------------------------------------------- #

# --- conftest.py ----------------------------------------- #
@pytest.fixture
def cli(aiohttp_client):
    from brainslug.webapp import process_agent_request
    app = web.Application()
    app.router.add_post('/channel/{lang}/{id}', process_agent_request)
    return asyncio.get_event_loop().run_until_complete(aiohttp_client(app))
# --- conftest.py ----------------------------------------- #


async def test_process_agent_request_not_found_whitout_parameters(cli):
    resp = await cli.post('/channel', data={})
    assert resp.status == 404, "must return not found if no parameters"

