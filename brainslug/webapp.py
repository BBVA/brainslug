import asyncio

from aiohttp import web
from tinydb import Query

from brainslug.languages import LANGUAGES
from brainslug import channel


def config_routes(app):
    app.add_routes([
        web.post('/channel/{__language__}/{__key__}', channel_input)
    ])


async def process_agent_request(language, key, meta, last_result):
    Q = Query()
    try:
        [document] = channel.CHANNELS.search(Q['__key__'] == key)
    except ValueError:
        document = meta.copy()
        document['__key__'] = key
        document['__language__'] = language
        document['__channel__'] = channel.Channel()
        await channel.CHANNELS.insert(document)
        await document['__channel__'].first_step()
    else:
        await document['__channel__'].next_step(last_result)


async def channel_input(request):
    try:
        lang = LANGUAGES[request.match_info['__language__']]
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
