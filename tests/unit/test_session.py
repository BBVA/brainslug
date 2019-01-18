import pytest

from brainslug import Session

def test_session_needs_some_parameters():
    with pytest.raises(TypeError):
        Session()

def test_session_store_attributes():
    agent_type = object()
    machine_id = object()
    process_id = object()

    session = Session(agent_type, machine_id, process_id)

    assert session.agent_type is agent_type
    assert session.machine_id is machine_id
    assert session.process_id is process_id
