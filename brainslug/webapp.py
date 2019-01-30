import asyncio

from aiohttp import web
from tinydb import Query

from brainslug.ribosomes import RIBOSOMES
from brainslug import channel


def config_routes(app):
    app.add_routes([
        web.post('/channel/{__ribosome__}/{__key__}', channel_input)
    ])


async def process_agent_request(ribosome, key, meta, last_result):
    Q = Query()
    try:
        [document] = channel.CHANNELS.search(Q['__key__'] == key)
    except ValueError:
        document = {**meta,
                    '__key__': key,
                    '__ribosome__': ribosome,
                    '__channel__': channel.Channel()}
        await channel.CHANNELS.insert(document)
        return await document['__channel__'].first_step()
    else:
        return await document['__channel__'].next_step(last_result)


async def channel_input(request):
    try:
        lang = RIBOSOMES[request.match_info['__ribosome__']]
    except KeyError:
        raise web.HTTPNotFound()
    key = request.match_info['__key__']
    meta = dict(request.rel_url.query)
    last_result = await request.read()
    next_code = await process_agent_request(lang, key, meta, last_result)
    return web.Response(body=next_code)


async def run_web_server():
    app = web.Application()
    config_routes(app)

    runner = web.AppRunner(app)
    await runner.setup()

    server = web.TCPSite(runner, 'localhost', 8080, shutdown_timeout=0)
    asyncio.create_task(server.start())

    return runner
