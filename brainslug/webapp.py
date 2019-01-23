from aiohttp import web
from brainslug.languages import LANGUAGES


def config_routes(app):
    app.add_routes([
            web.post('/channel/{__language__}/{__key__}', channel_input)
    ])


async def process_agent_request(language, key, meta, last_result):
    pass


async def channel_input(request):
    try:
        lang = LANGUAGES[request.match_info['__language__']]
    except KeyError:
        raise web.HTTPNotFound()
    key = request.match_info['__key__']
    meta = dict(request.rel_url.query)
    last_result = await request.read()
    if not last_result:
        last_result = None
    await process_agent_request(lang, key, meta, last_result)
    return web.Response()
