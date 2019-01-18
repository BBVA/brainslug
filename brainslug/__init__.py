"""
Contains the application runtime primitives and the global state.

"""
import asyncio
import weakref
import dataclasses

from brainslug.utils import SyncedVar

# Global application state
SESSIONS = weakref.WeakValueDictionary()


@dataclasses.dataclass
class Session:
    """
    Manage the communication channel among one agent and one or more
    zombie instances.

    """
    agent_type: object
    machine_id: object
    process_id: object

    _code = SyncedVar()
    _result = SyncedVar()

    async def remote_eval(self, code):
        """
        Arrange the execution of `code` in the remote agent, returning
        it result eventually.

        """
        self._code = code
        return await self._result

    async def first_step(self):
        """Return the first code to be evaluated by the remote agent."""
        return await self._code

    async def next_step(self, last_result):
        """
        Receive the result of the last evaluation and return the next
        code to evaluate.

        """
        self._result = last_result
        return await self._code
