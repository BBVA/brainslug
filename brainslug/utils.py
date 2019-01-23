"""
Miscelaneous utilities for brainslug.

"""
import asyncio


def to_remote(loop, doc):
    remote = doc['__language__']
    channel = doc['__channel__']

    def _run_threadsafe(code):
        return asyncio.run_coroutine_threadsafe(
            channel.remote_eval(code), loop).result()

    return remote(_run_threadsafe)


def get_resources(loop, store, spec):
    resources = dict()

    for name, query in spec.items():
        found = store.search(query)
        if found:
            # TODO: Implement Many() to return a list
            resources[name] = to_remote(loop, found[0])
        else:
            return None

    return resources


async def wait_for_resources(loop, store, spec):
    resources = get_resources(loop, store, spec)
    while resources is None:
        await store.wait_for_new_channel()
        resources = get_resources(loop, store, spec)
    return resources
