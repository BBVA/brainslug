"""
Contains the application runtime primitives and the global state.

"""
import asyncio

from tinydb import Query

from brainslug import webapp
from brainslug import channel
from brainslug import _slug

__all__ = ['Brain', 'slug', 'run']

#: Used to query for resources
Brain = Query()

#: Decorator for slug definition
slug = _slug.Slug.create


def run(slug):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_slug.run_slug(slug))
