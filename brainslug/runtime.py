from brainslug.database import AsyncTinyDB
from brainslug.remote import Remote

#: Global application state
AGENT_INFO = AsyncTinyDB()


def get_resources(loop, store, spec):
    resources = dict()

    for name, query in spec.items():
        found = store.search(query)
        if found:
            # TODO: Implement Many() to return a list
            agent_info = found[0]
            resources[name] = Remote.from_agent_info(loop, agent_info)
        else:
            return None

    return resources


async def wait_for_resources(loop, store, spec):
    resources = get_resources(loop, store, spec)
    while resources is None:
        await store.wait_for_insert()
        resources = get_resources(loop, store, spec)
    return resources
