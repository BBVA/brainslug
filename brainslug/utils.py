"""
Miscelaneous utilities for brainslug.

"""
import asyncio


class SyncedVar:
    """
    A variable synced using an asyncio.Event.

    >>> class Foo:
    ...     bar = SyncedVar()
    >>> foo = Foo()

    Setting a SyncedVar value is a synchronous operation::
    >>> foo.bar = 'myvalue'

    Getting a SyncedVar value is an asynchonous operation::
    >>> asyncio.get_event_loop().run_until_complete(foo.bar)
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
