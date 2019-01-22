from abc import ABCMeta, abstractmethod
import time
from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools
import json
import operator as op
import sys
import threading
import traceback
import uuid
import weakref

from aiohttp import web

from tinydb.middlewares import Middleware
from tinydb.storages import MemoryStorage
from tinydb import TinyDB, Query


# ✂ - brainslug/__init__.py ------------------------------------- ✂

RUNNING = dict()
SESSIONS = TinyDB(storage=MemoryStorage)
LANGUAGES = dict()  # name: transpiler
Q = Query()

# ✂ - brainslug/webapp.py --------------------------------------- ✂

#
# Endpoints
#
async def process_agent_request(request):
    """
    Validate the arriving data from the agent and return new code to
    evaluate or an error.

    """
    try:
        language = LANGUAGES[request.match_info['__language__']]
    except KeyError:
        raise web.HTTPNotFound('Unknown language')
    else:
        next_code = await last_result_just_arrived(
            key=request.match_info['__key__'],
            language=language,
            meta=dict(request.rel_url.query),
            last_result=await request.read())
        return web.Response(text=next_code)

#
# Runtime
#
async def last_result_just_arrived(key, language, meta, last_result):
    """
    Receive some new last_result from the remote agent and return the
    code.

    """
    try:
        session = SESSIONS.search(Q['__key__'] == key)[0]
    except IndexError:
        session = meta.copy()
        session['__key__'] = key
        session['__channel__'] = Channel()
        session['__language__'] = language
        SESSIONS.insert(session)
        return (await session['__channel__'].first_step())
    else:
        return (await session['__channel__'].next_step(last_result))


class SyncedVar:
    """
    A variable synced using an asyncio.Event.

    A SyncedVar is a data-descriptor. Therefore is used as a class
    property.
        >>> class Foo:
        ...     bar = SyncedVar()

    On the instances...
        >>> foo = Foo()

    Setting the value is a synchronous operation:
        >>> foo.bar = 'myvalue'

    Getting the value is an asynchonous operation:
        >>> loop = asyncio.get_event_loop()
        >>> loop.run_until_complete(foo.bar)
        'myvalue'

    """
    def get_value(self, instance):
        """Return the stored value from the instance."""
        name = f"__syncvar_{id(self)}_value"
        if not hasattr(instance, name):
            setattr(instance, name, None)
        return getattr(instance, name)

    def set_value(self, instance, value):
        """Set the stored value from the instance."""
        return setattr(instance, f"__syncvar_{id(self)}_value", value)

    def get_event(self, instance):
        """Get the Event object used for synchronization."""
        name = f"__syncvar_{id(self)}_event"
        if not hasattr(instance, name):
            setattr(instance, name, asyncio.Event())
        return getattr(instance, name)

    def __get__(self, instance, owner):
        """
        Return a coroutine object who waits for the event before
        returning the value.

        .. important::
           The returned value has to be awaited.

        """
        async def wait_for_value():
            await self.get_event(instance).wait()
            self.get_event(instance).clear()
            return self.get_value(instance)
        return wait_for_value()

    def __set__(self, instance, value):
        """Set the value and the event."""
        self.set_value(instance, value)
        self.get_event(instance).set()

class Channel:
    """
    Manage the communication channel between an agent and one or more
    zombie instances.

    """

    _code = SyncedVar()
    _result = SyncedVar()

    def __init__(self):
        self._eval_lock = asyncio.Lock()

    async def remote_eval(self, code):
        """
        Arrange the execution of `code` on the remote agent, eventually
        returning its result.

        """
        async with self._eval_lock:
            self._code = code
            return await self._result

    async def first_step(self):
        """Return the first code to be evaluated by the remote agent."""
        return await self._code

    async def next_step(self, last_result):
        """
        Receive the result of the last evaluation and return the next
        code to evaluate eventually.

        """
        self._result = last_result
        return await self._code


class Remote(metaclass=ABCMeta):
    def __init__(self, remote_eval):
        self.remote_eval = remote_eval

    @abstractmethod
    def listdir(self, path):
        pass


class PythonRemote(Remote):
    def listdir(self, path):
        res = self.remote_eval("""
import os
os.listdir()
""")
        return json.loads(res.decode('utf-8'))


class PowerShellRemote(Remote):
    def listdir(self, path):
        res = json.loads(self.remote_eval(json.dumps(f'dir "{path}"')))
        if isinstance(res, list):
            return reversed([x["Name"] for x in res])
        else:
            return [res["Name"]]

# ✂ - brainslug/__init__.py ------------------------------------- ✂

LANGUAGES["powershell"] = PowerShellRemote
LANGUAGES["python"] = PythonRemote


# ✂ - brainslug/app.py ------------------------------------------ ✂

class BrainslugApp:
    def __init__(self, fn, spec):
        self._fn = fn
        self.spec = spec

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)


def brainslugapp(**spec):
    def _brainslugapp(fn):
        return BrainslugApp(fn=fn, spec=spec)
    return _brainslugapp

#
# Available apps
#


# ✂ - brainslug/__main__.py ------------------------------------- ✂
def run_in_rt(coro, loop):
    return asyncio.run_coroutine_threadsafe(coro, loop).result()

async def prepare(fn):
    # Espera a que a estén todos los recursos que pide `fn`.
    loop = asyncio.get_event_loop()
    resources = None
    while fn.spec and resources is None:
        _resources = dict()
        for name, query in fn.spec.items():
            found = SESSIONS.search(query)
            if not found:
                break
            else:
                doc = found[0]
                remote = doc['__language__']
                channel = doc['__channel__']
                _resources[name] = remote(
                    lambda code: run_in_rt(channel.remote_eval(code), loop))
        else:
            resources = _resources
            break

        # print("Waiting for workers...")
        await asyncio.sleep(1)
    return functools.partial(fn, **resources)


async def run_in_thread(fn):
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        await asyncio.get_event_loop().run_in_executor(executor, fn)
    except Exception:
        _, _, tb = sys.exc_info()
        return tb
    else:
        return None

async def run_user_app(fn):
    await run_in_thread(await prepare(fn))

async def runner(fn, app):
    await run_user_app(fn)
    asyncio.get_event_loop().create_task(app.cleanup())


async def start_background_brainslug(fn, app):
    loop = asyncio.get_event_loop()
    app['brainslug_task'] = loop.create_task(runner(fn, app))

async def cleanup_background_task(app):
    exc = await app['brainslug_task']
    if exc is not None:
        traceback.print_tb(exc)
        sys.exit(1)
    else:
        sys.exit(0)

def run(fn):
    # TODO: refactor
    app = web.Application()
    app.add_routes([
        web.post('/channel/{__key__}/{__language__}',
                 process_agent_request),
        # web.post('/boot/{__language__}/{__key__}'),
    ])

    app.on_startup.append(functools.partial(start_background_brainslug, fn))
    app.on_cleanup.append(cleanup_background_task)

    web.run_app(app, print=None)


# # --------------------------------------------------------------- ✂
# # Ejemplo de Applicacion                                          ✂
# # --------------------------------------------------------------- ✂


# import brainslug

@brainslugapp(pepe=((Q.hostname == 'pepe') & (Q.platform == 'linux')))
def list_current_dir(pepe):
    for path in ['.', '..', '/tmp']:
        for filename in pepe.listdir(path):
            print(path, filename)

if __name__ == '__main__':
    run(list_current_dir)

# # - Ejemplo de interfaz -------------------------
# from brainslug import language

# java = language('java')

# @java('os.listdir')
# def llll(remote, path):
#     if remote.remote_eval('mis') == 'akkaka':
#         raise FileNotFoundError()


# METHODS[('java', 'os.listdir')] = llll
