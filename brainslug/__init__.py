from argparse import Namespace
import asyncio
import sys

from tinydb import Query

from brainslug import _slug
from brainslug.banner import BANNER

__all__ = ['body', 'slug', 'run']

#: Used to query for resources
body = Query()

#: Decorator for slug definition
slug = _slug.Slug.create


def run(slug, local=False):
    print(BANNER)
    if local:
        resources = dict()
        for name in slug.spec:
            resources[name] = Namespace(**sys.modules)
        return slug.fn(**resources)
    else:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_slug.run_slug(slug))
