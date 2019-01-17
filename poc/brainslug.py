from abc import ABCMeta, abstractmethod
from functools import partial
import asyncio
import json
import threading
import uuid
import weakref

from aiohttp import web

# ✂ - brainslug/__init__.py ------------------------------------- ✂

# XXX: Cada mochuelo a su olivo
APPS = dict()
RUNNING = dict()
SESSIONS = weakref.WeakValueDictionary()
ZOMBIE_TYPES = dict()

# ✂ - brainslug/webapp.py --------------------------------------- ✂

#
# Endpoints
#

async def process_agent_request(request):
    """
    Validate the arriving data from the agent and return new code to
    evaluate or an error.

    """
    # TODO: Verify `agent_type`, `machine_id` and `process_id` format.
    last_result = await request.read()

    # print("last_result", last_result)
    next_code = await last_result_just_arrived(
        agent_type=request.match_info["agent_type"],
        machine_id=request.match_info["machine_id"],
        process_id=request.match_info["process_id"],
        last_result=last_result)
    # print("next_code", next_code)

    return web.Response(text=next_code)


async def list_apps(request):
    return web.json_response(list(APPS.keys()))


async def run_app(request):
    app_name = request.match_info["app_name"]
    fn = APPS[app_name]
    return web.json_response(run(fn))


async def get_process_state(request):
    pid = request.match_info["pid"]
    process = RUNNING[pid]
    return web.json_response(process.state)


async def input_process(request):
    pid = request.match_info["pid"]
    process = RUNNING[pid]
    process.state.user_input = await request.read()


# ✂ - brainslug/__init__.py ------------------------------------- ✂

#
# Runtime
#
async def last_result_just_arrived(agent_type, machine_id, process_id,
                                   last_result):
    """
    Receive some new last_result from the remote agent and return the
    code.

    """
    key = (agent_type, machine_id, process_id)

    try:
        session = SESSIONS[key]
    except KeyError:
        session = SESSIONS[key] = Session(agent_type, machine_id,
                                          process_id)

    return (await session.next_step(last_result))



class Session:
    def __init__(self, agent_type, machine_id, process_id):
        self.agent_type = agent_type
        self.machine_id = machine_id
        self.process_id = process_id

        self.last_result_has_data = asyncio.Event()
        self.last_result_content = None

        self.next_step_write = asyncio.Lock()
        self.next_step_has_data = asyncio.Event()
        self.next_step_content = None

        self.is_first = True

    @property
    def agent_id(self):
        return (self.agent_type, self.machine_id, self.process_id)

    def __hash__(self):
        return hash(self.agent_id)

    async def remote_eval(self, code):
        """
        Eval a foreign code in the remote agent and returning the
        result.

        """
        async with self.next_step_write:
            self.next_step_content = code
            self.next_step_has_data.set()

            await self.last_result_has_data.wait()
            return self.last_result_content


    async def next_step(self, last_result):
        """
        Given the result of the last computation, return the next code
        to compute.

        """
        # Deliver the last result
        if not self.is_first:
            self.last_result_content = last_result
            self.last_result_has_data.set()

        self.is_first = False

        # Deliver the next computation
        await self.next_step_has_data.wait()
        return self.next_step_content


# ✂ - brainslug/userapi.py -------------------------------------- ✂

class UserAPI(dict):
    def __init__(self, *args, **kwargs):
        self.user_input = None
        super().__init__(*args, **kwargs)

    def wait_for_input(self):
        """Called from the app, waits for the next input."""
        pass

    def add_input_from_outside(self, data):
        """...waking the sleep app."""
        pass


# ✂ - brainslug/zombie.py --------------------------------------- ✂

class Zombie(metaclass=ABCMeta):
    def __init__(self, remote_eval):
        self.remote_eval = remote_eval

    @abstractmethod
    def listdir(self, path):
        pass


class PythonZombie(Zombie):
    def listdir(self, path):
        res = self.remote_eval("""
import os
os.listdir()
""")
        return json.loads(res.decode('utf-8'))


class PowerShellZombie(Zombie):
    def listdir(self, path):
        res = json.loads(self.remote_eval(json.dumps("dir")))
        if isinstance(res, list):
            return reversed([x["Name"] for x in res])
        else:
            return [res["Name"]]

# ✂ - brainslug/__init__.py ------------------------------------- ✂

ZOMBIE_TYPES["powershell"] = PowerShellZombie
ZOMBIE_TYPES["python"] = PythonZombie


class ZombieSpec(dict):
    def match(self, session):
        return True

    def get_best(self, session_list):
        for session in session_list:
            if self.match(session):
                return session
        raise ValueError("Can't match any zombie.")


class Process:
    def __init__(self, fn, userapi, **kwargs):
        self.state = userapi
        self.thread = threading.Thread(target=fn, args=[userapi], kwargs=kwargs)
        self.thread.start()


def run(fn):
    zombies = dict()

    loop = asyncio.get_event_loop()
    for name, filter in fn.spec.items():
        session = filter.get_best(SESSIONS.values())

        remote_eval = lambda code: asyncio.run_coroutine_threadsafe(session.remote_eval(code), loop).result()

        # import ipdb
        # ipdb.set_trace()
        ZombieClass = ZOMBIE_TYPES[session.agent_type]
        zombies[name] = ZombieClass(remote_eval)

    # ✂ ------------------------------------------------------------- ✂

    pid = str(uuid.uuid4())

    userapi = UserAPI()
    RUNNING[pid] = Process(fn, userapi, **zombies)

    return pid

# ✂ - brainslug/app.py ------------------------------------------ ✂

class ZombieApp:
    def __init__(self, fn, spec):
        self._fn = fn
        self.spec = spec

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)


def zombieapp(**spec):
    def _zombieapp(fn):
        app = ZombieApp(fn=fn, spec=spec)
        APPS[fn.__name__] = app
        return app
    return _zombieapp


#
# Available apps
#

# ✂ - brainslug/pocapps.py -------------------------------------- ✂

@zombieapp(z=ZombieSpec(machine_id='pepe', platform='linux'))
def list_current_dir(userapi, z):
    res = z.listdir(".")
    print(res)
    userapi["out"] = res

# ✂ - brainslug/__main__.py ------------------------------------- ✂

if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.post('/next-code/{agent_type}/{machine_id}/{process_id}',
                 process_agent_request),
        web.get('/app', list_apps),
        web.put('/app/run/{app_name}', run_app),
        web.get('/pid/{pid}', get_process_state),
        web.post('/pid/{pid}', input_process),
    ])
    web.run_app(app)
