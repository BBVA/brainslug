
# --- objects --------------------------------------------- #
def test_process_agent_request_exists():
    try:
        from brainslug.webapp import process_agent_request
    except ImportError as exc:
        assert False, exc


def test_process_agent_request_is_a_function():
    from brainslug.webapp import process_agent_request
    assert callable(process_agent_request), "process_agent_request must be a function"
# --- objects --------------------------------------------- #