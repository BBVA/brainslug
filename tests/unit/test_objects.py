import importlib
from tinydb import TinyDB, Query
import pytest


@pytest.mark.parametrize('module_name, name',
                         [('brainslug', 'body'),
                          ('brainslug._slug', 'Slug'),
                          ('brainslug._slug', 'run_slug'),
                          ('brainslug.channel', 'Channel'),
                          ('brainslug.channel', 'SyncedVar'),
                          ('brainslug.database', 'AsyncTinyDB'),
                          ('brainslug.remote', 'Remote'),
                          ('brainslug.ribosome', 'RIBOSOMES'),
                          ('brainslug.ribosome', 'Symbol'),
                          ('brainslug.ribosome', 'define'),
                          ('brainslug.runtime', 'AGENT_INFO'),
                          ('brainslug.runtime', 'get_resources'),
                          ('brainslug.runtime', 'wait_for_resources'),
                          ('brainslug.web', 'config_routes'),
                          ('brainslug.web', 'process_agent_request'),
                          ('brainslug.web', 'run_web_server')])
def test_object_is_importable(module_name, name):
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        assert False, exc
    else:
        assert hasattr(module, name), \
               f"Object {name} not found in module {module_name}"


def test_agent_info_is_a_asynctinydb_instance():
    from brainslug.runtime import AGENT_INFO
    from brainslug.database import AsyncTinyDB
    assert isinstance(AGENT_INFO, AsyncTinyDB)


def test_brain_is_a_query():
    from brainslug import body
    assert Query in body.__mro__
