import inspect
import weakref


def test_channel_exist():
    try:
        from brainslug import Channel
    except ImportError as exc:
        assert False, exc


def test_channel_is_a_class():
    from brainslug import Channel
    assert inspect.isclass(Channel)


def test_channels_exists():
    try:
        from brainslug import CHANNELS
    except ImportError as exc:
        assert False, exc


def test_channels_is_a_weakvaluedictionary():
    from brainslug import CHANNELS
    assert isinstance(CHANNELS, weakref.WeakValueDictionary)


def test_syncedvar_exists():
    try:
        from brainslug.utils import SyncedVar
    except ImportError as exc:
        assert False, exc


def test_syncedvar_is_a_class():
    from brainslug.utils import SyncedVar
    assert inspect.isclass(SyncedVar)


def test_syncedvar_is_a_data_descriptor():
    from brainslug.utils import SyncedVar
    assert hasattr(SyncedVar, '__set__')
    assert hasattr(SyncedVar, '__get__')
