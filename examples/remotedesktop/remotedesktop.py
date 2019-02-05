from aiohttp import web
from brainslug import run
from brainslug import slug, body
import __main__
from functools import partial
import aiohttp
import asyncio
import base64
import json
import mss

import logging, sys
from autologging import TRACE
logging.basicConfig(level=TRACE, stream=sys.stdout,
    format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")


async def process_events(websocket, remote):
    async for message in websocket:
        if message.type == aiohttp.WSMsgType.TEXT:
            message = json.loads(message.data)
            if message['type'] == 'click':
                # TODO: remote click
                print("click", message['x'], message['y'])
            elif message['type'] == 'mousemove':
                # TODO: mouse move
                print("mousemove", message['x'], message['y'])
            elif message['type'] == 'keypress':
                # TODO: send key
                print("keypress", message['k'])
            else:
                raise TypeError('Unknown message type %r' %
                                message['type'])
        else:
            return

async def index(request):
    return web.FileResponse('./index.html')


async def manage_websocket(remote, request):
    websocket = web.WebSocketResponse()
    await websocket.prepare(request)
    queue = asyncio.Queue()
    asyncio.create_task(process_events(websocket, remote))
    loop = asyncio.get_event_loop()
    with remote.mss.mss() as scr:
        while True:
            filename = await loop.run_in_executor(None, scr.shot)
            with open(filename, 'rb') as screenshot:
                base64image = base64.b64encode(screenshot.read())
                await websocket.send_str(base64image.decode('ascii'))


@slug(remote=body.__key__ == 'pepe')
def remotedesktop(remote):
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = web.Application()
    app.add_routes([
        web.get('/', index),
        web.get('/ws', partial(manage_websocket, remote))
    ])
    web.run_app(app, port=8091, handle_signals=False)


if __name__ == '__main__':
    import ribosome
    run(remotedesktop, local=False)
