from contextlib import suppress
from unittest.mock import patch, Mock
import asyncio
import warnings

from aiohttp import web
import pytest

from brainslug._slug import run_slug
from brainslug._slug import Slug
from brainslug.webapp import config_routes as real_config_routes
from brainslug.webapp import run_web_server


@pytest.mark.asyncio
async def test_run_web_server_configures_the_app(event_loop):
    with patch('brainslug.webapp.config_routes',
               wraps=real_config_routes) as config_routes:
        runner = await run_web_server()
        config_routes.assert_called_once()
        await runner.cleanup()


@pytest.mark.asyncio
async def test_run_web_server_spawn_a_server_task(event_loop):
    with patch('asyncio.create_task') as create_task:
        with patch('aiohttp.web.TCPSite') as TCPSite:
            await run_web_server()
            TCPSite.assert_called_once()
            create_task.assert_called_once_with(TCPSite().start())


@pytest.mark.asyncio
async def test_run_web_server_returns_the_runner(event_loop):
    with patch('asyncio.create_task') as create_task:
        with patch('aiohttp.web.TCPSite'):  # To avoid warning :(
            runner = await run_web_server()
            assert isinstance(runner, web.AppRunner)


@pytest.mark.asyncio
async def test_run_slug_returns_slug_result(event_loop):
    result = object()

    @Slug.create()
    def foo():
        return result

    assert await run_slug(foo) is result


@pytest.mark.asyncio
async def test_run_slug_starts_the_web_server(event_loop):
    async def ret_runner():
        runner = Mock()
        runner.cleanup.return_value = asyncio.sleep(0)
        return runner
    with patch('brainslug.webapp.run_web_server') as run_web_server:
        run_web_server.return_value = ret_runner()
        await run_slug(Slug(lambda: None, {}))
        run_web_server.assert_called_once()


@pytest.mark.asyncio
async def test_run_slug_stops_the_web_server_at_exit(event_loop):
    @Slug.create()
    def foo():
        raise Exception

    runner = Mock()

    async def ret_runner():
        return runner

    with patch('brainslug.webapp.run_web_server') as run_web_server:
        run_web_server.return_value = ret_runner()
        with suppress(Exception):
            await run_slug(Slug(foo, {}))
        runner.cleanup.assert_called_once()
