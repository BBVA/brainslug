from brainslug import webapp
import aiohttp


def test_config_routes_is_a_function():
    assert callable(webapp.config_routes), "config routes must be a function"


def test_config_routes_return_the_same_app():
    origin = aiohttp.web.Application()
    assert webapp.config_routes(origin) is origin, "config routes must return the same app"

async def test_process_agent_request_not_found_whitout_parameters(cli):
    resp = await cli.post('/channel', data={})
    assert resp.status == 404, "must return not found if no parameters"
