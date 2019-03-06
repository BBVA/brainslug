import asyncio
from uuid import uuid4
import os

from aiohttp import web
from tinydb import Query
import aiohttp_cors

from brainslug import runtime
from brainslug.ribosome import RIBOSOMES, Symbol
from brainslug.channel import Channel


def config_routes(app):
    app.add_routes([
        web.post('/channel/{__ribosome__}/{__key__}', channel_input),
        web.get('/launch/{__ribosome__}', get_launch),
        web.get('/boot/{__ribosome__}', get_boot),
        web.get('/boot/{__ribosome__}/{__key__}', get_boot)
    ])
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
    })
    for resource in app.router.resources():
        cors.add(resource)


async def process_agent_request(ribosome, key, meta, last_result):
    Q = Query()
    try:
        [document] = runtime.AGENT_INFO.search(Q['__key__'] == key)
    except ValueError:
        document = {**meta,
                    '__key__': key,
                    '__ribosome__': ribosome,
                    '__channel__': Channel()}
        await runtime.AGENT_INFO.insert(document)
        return await document['__channel__'].first_step()
    else:
        return await document['__channel__'].next_step(last_result)


async def channel_input(request):
    ribosome = request.match_info['__ribosome__']
    key = request.match_info['__key__']
    meta = dict(request.rel_url.query)
    last_result = await request.read()

    next_code = await process_agent_request(ribosome, key, meta, last_result)

    return web.Response(body=next_code)


async def get_boot(request):
    ribosome = request.match_info['__ribosome__']
    key = request.match_info.get('__key__', str(uuid4()))
    try:
        boot = RIBOSOMES[Symbol((ribosome, 'boot'))]
    except KeyError as exc:
        raise web.HTTPNotFound() from exc
    else:
        url = request.url
        url = request.url.with_path(f'/channel/{ribosome}/{key}')
        url = url.with_query(request.url.query)
        return web.Response(body=boot(remote=None, url=url,
                                      **request.rel_url.query))


async def get_launch(request):
    ribosome = request.match_info['__ribosome__']
    try:
        launch = RIBOSOMES[Symbol((ribosome, 'launch'))]
    except KeyError as exc:
        raise web.HTTPNotFound() from exc
    else:
        url = request.url
        url = request.url.with_path(f'/boot/{ribosome}')
        url = url.with_query(request.url.query)
        return web.Response(body=launch(remote=None, url=url,
                                        **request.rel_url.query),
                            content_type="text/html")


async def run_web_server():
    app = web.Application(client_max_size=None)
    config_routes(app)

    runner = web.AppRunner(app)
    await runner.setup()

    server = web.TCPSite(runner,
                         os.environ.get('BRAINSLUG_HOST', '0.0.0.0'),
                         int(os.environ.get('BRAINSLUG_PORT', '8080')),
                         shutdown_timeout=0)
    asyncio.create_task(server.start())

    return runner
