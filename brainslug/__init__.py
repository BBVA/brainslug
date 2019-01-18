"""
Contains the application runtime primitives and the global state.

"""
import asyncio
import weakref


# Global application state
SESSIONS = weakref.WeakValueDictionary()


class Session:
    """
    Manage the communication channel among one agent and one or more
    zombie instances.

    """
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
        """
        Return a coroutine object who waits for the code to arrive.

        .. important::
           The returned object has to be awaited.

        """
        async def get_code():
            """Wait for the code to arrive and return it."""
            await self._code_event.wait()
            self._code_event.clear()
            return self._code_value
        return get_code()

    @code.setter
    def code(self, value):
        """Store the code and flag its arrival."""
        self._code_value = value
        self._code_event.set()

    @property
    def result(self):
        """
        Return a coroutine object who waits for the result to arrive.

        .. important::
           The returned object has to be awaited.

        """
        async def get_result():
            """Wait for the result to arrive and return it."""
            await self._result_event.wait()
            self._result_event.clear()
            return self._result_value
        return get_result()

    @result.setter
    def result(self, value):
        """Store the result and flag its arrival."""
        self._result_value = value
        self._result_event.set()

    async def remote_eval(self, code):
        """
        Arrange the execution of `code` in the remote agent, returning
        it result eventually.

        """
        self.code = code
        return await self.result

    async def first_step(self):
        """Return the first code to be evaluated by the remote agent."""
        return await self.code

    async def next_step(self, last_result):
        """
        Receive the result of the last evaluation and return the next
        code to evaluate.

        """
        self.result = last_result
        return await self.code
