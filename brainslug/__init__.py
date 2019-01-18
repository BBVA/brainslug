import asyncio
import weakref


SESSIONS = weakref.WeakValueDictionary()


class Session:
    def __init__(self, agent_type, machine_id, process_id):
        self.agent_type = agent_type
        self.machine_id = machine_id
        self.process_id = process_id

        self.code = None
        self.code_available = asyncio.Event()

        self.result = None
        self.result_available = asyncio.Event()

    async def remote_eval(self, code):
        self.code = code
        self.code_available.set()
        await self.result_available.wait()
        return self.result

    async def first_step(self):
        await self.code_available.wait()
        return self.code

    async def next_step(self, last_result):
        self.result = last_result
        self.result_available.set()
        await asyncio.sleep(2)
