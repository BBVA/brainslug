import inspect

def test_session_exist():
    try:
        from brainslug import Session
    except ImportError as exc:
        assert False, exc


def test_session_is_a_class():
    from brainslug import Session
    assert inspect.isclass(Session)
