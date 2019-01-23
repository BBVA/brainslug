from aiohttp import web


def config_routes(app):
    app.add_routes([
            web.post('/channel/{__language__}/{__key__}', channel_input)
    ])


async def process_agent_request(language, key, meta, last_result):
    pass


async def channel_input(request):
    lang = request.match_info['__language__']
    key = request.match_info['__key__']
    await process_agent_request(lang, key, None, None)
    return web.Response()
