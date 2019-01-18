
# --- objects --------------------------------------------- #
def test_process_agent_request_exists():
    try:
        from brainslug.webapp import process_agent_request
    except ImportError as exc:
        assert False, exc
# --- objects --------------------------------------------- #