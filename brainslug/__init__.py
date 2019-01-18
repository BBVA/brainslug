import asyncio
import weakref


SESSIONS = weakref.WeakValueDictionary()


class Session:
    def __init__(self, agent_type, machine_id, process_id):
        self.agent_type = agent_type
        self.machine_id = machine_id
        self.process_id = process_id

        self._code_value = None
        self._code_event = asyncio.Event()

        self._result_value = None
        self._result_event = asyncio.Event()

    @property
    def code(self):
        async def get_code():
            await self._code_event.wait()
            self._code_event.clear()
            return self._code_value
        return get_code


    @code.setter
    def code(self, value):
        self._code_value = value
        self._code_event.set()

    @property
    def result(self):
        async def get_result():
            await self._result_event.wait()
            self._result_event.clear()
            return self._result_value
        return get_result

    @result.setter
    def result(self, value):
        self._result_value = value
        self._result_event.set()

    async def remote_eval(self, code):
        self.code = code
        return await self.result()

    async def first_step(self):
        return await self.code()

    async def next_step(self, last_result):
        self.result = last_result
        return await self.code()
