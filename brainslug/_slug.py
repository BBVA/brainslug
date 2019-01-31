import asyncio
import functools

from concurrent.futures import ThreadPoolExecutor

from brainslug import web
from brainslug import runtime
from brainslug import ribosome


class Slug:
    def __init__(self, fn, spec):
        self.fn = fn
        self.spec = spec

    @classmethod
    def create(cls, **spec):
        return functools.partial(Slug, spec=spec)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    async def run_in_thread(self, loop, fn):
        executor = ThreadPoolExecutor(max_workers=1)
        return await loop.run_in_executor(executor, fn)

    async def attach_resources(self, loop):
        resources = await runtime.wait_for_resources(loop,
                                                     runtime.AGENT_INFO,
                                                     self.spec)
        return functools.partial(self.fn, **resources)

    async def run(self):
        loop = asyncio.get_event_loop()
        prepared = await self.attach_resources(loop)
        return await self.run_in_thread(loop, prepared)


async def run_slug(slug):
    ribosome.load()
    runner = await web.run_web_server()
    try:
        return await slug.run()
    finally:
        await runner.cleanup()
