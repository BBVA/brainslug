"""
Miscelaneous utilities for brainslug.

"""
import asyncio


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


def to_remote(loop, doc):
    remote = doc['__language__']
    channel = doc['__channel__']

    def _run_threadsafe(code):
        return asyncio.run_coroutine_threadsafe(
            channel.remote_eval(code), loop).result()

    return remote(_run_threadsafe)


def get_resources(loop, store, spec):
    resources = dict()
    for name, query in spec.items():
        found = store.search(query)
        if found:
            # TODO: Implement MANY to return a list
            resources[name] = to_remote(loop, found[0])
        else:
            return None
    return resources
