import inspect
import weakref


def test_session_exist():
    try:
        from brainslug import Session
    except ImportError as exc:
        assert False, exc


def test_session_is_a_class():
    from brainslug import Session
    assert inspect.isclass(Session)


def test_sessions_exists():
    try:
        from brainslug import SESSIONS
    except ImportError as exc:
        assert False, exc


def test_sessions_is_a_weakvaluedictionary():
    from brainslug import SESSIONS
    assert isinstance(SESSIONS, weakref.WeakValueDictionary)


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
