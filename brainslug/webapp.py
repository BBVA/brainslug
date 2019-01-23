from aiohttp import web


def config_routes(app):
    app.add_routes([
            web.post('/channel/{__language__}/{__key__}', channel_input)
    ])


async def process_agent_request():
    pass


async def channel_input(request):
    await process_agent_request()
    return web.Response()
