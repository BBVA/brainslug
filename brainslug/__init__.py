import asyncio
import weakref


SESSIONS = weakref.WeakValueDictionary()


class Session:
    def __init__(self, agent_type, machine_id, process_id):
        self.agent_type = agent_type
        self.machine_id = machine_id
        self.process_id = process_id

        self._code = None
        self._code_available = asyncio.Event()

        self._result = None
        self._result_available = asyncio.Event()

    async def _get_code(self):
        await self._code_available.wait()
        self._code_available.clear()
        return self._code

    def _set_code(self, value):
        self._code = value
        self._code_available.set()

    async def _get_result(self):
        await self._result_available.wait()
        self._result_available.clear()
        return self._result

    def _set_result(self, value):
        self._result = value
        self._result_available.set()

    async def remote_eval(self, code):
        self._set_code(code)
        return await self._get_result()

    async def first_step(self):
        return await self._get_code()

    async def next_step(self, last_result):
        self._set_result(last_result)
        return await self._get_code()
