from unittest.mock import patch
import warnings

from aiohttp import web
import pytest

from brainslug import run_web_server
from brainslug.webapp import config_routes as real_config_routes


@pytest.mark.asyncio
async def test_run_web_server_configures_the_app(event_loop):
    with patch('brainslug.webapp.config_routes',
               wraps=real_config_routes) as config_routes:
        await run_web_server()
        config_routes.assert_called_once()


@pytest.mark.asyncio
async def test_run_web_server_spawn_a_server_task(event_loop_nowarn):
    with patch('asyncio.create_task') as create_task:
        with patch('aiohttp.web.TCPSite') as TCPSite:
            await run_web_server()
            TCPSite.assert_called_once()
            create_task.assert_called_once_with(TCPSite().start())


@pytest.mark.asyncio
async def test_run_web_server_returns_the_runner(event_loop_nowarn):
    with patch('asyncio.create_task') as create_task:
        with patch('aiohttp.web.TCPSite'):  # To avoid warning :(
            assert isinstance(await run_web_server(), web.AppRunner)
