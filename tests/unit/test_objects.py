import weakref

from tinydb import TinyDB


def test_channel_exist():
    try:
        from brainslug import Channel
    except ImportError as exc:
        assert False, exc


def test_channels_exists():
    try:
        from brainslug import CHANNELS
    except ImportError as exc:
        assert False, exc


def test_channels_is_a_tinydb_instance():
    from brainslug import CHANNELS
    assert isinstance(CHANNELS, TinyDB)


def test_syncedvar_exists():
    try:
        from brainslug.utils import SyncedVar
    except ImportError as exc:
        assert False, exc


def test_syncedvar_is_a_data_descriptor():
    from brainslug.utils import SyncedVar
    assert hasattr(SyncedVar, '__set__')
    assert hasattr(SyncedVar, '__get__')


def test_slug_exist():
    try:
        from brainslug import Slug
    except ImportError as exc:
        assert False, exc
