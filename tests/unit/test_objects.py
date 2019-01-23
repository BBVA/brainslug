import importlib
from tinydb import TinyDB, Query
import pytest


@pytest.mark.parametrize('module_name, name',
                         [('brainslug', 'Channel'),
                          ('brainslug', 'CHANNELS'),
                          ('brainslug.languages', 'LANGUAGES'),
                          ('brainslug', 'ChannelStorage'),
                          ('brainslug.utils', 'SyncedVar'),
                          ('brainslug.utils', 'to_remote'),
                          ('brainslug.utils', 'get_resources'),
                          ('brainslug.utils', 'wait_for_resources'),
                          ('brainslug', 'Brain'),
                          ('brainslug', 'run_web_server'),
                          ('brainslug.webapp', 'process_agent_request'),
                          ('brainslug.webapp', 'config_routes'),
                          ('brainslug', 'Slug')])
def test_object_is_importable(module_name, name):
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        assert False, exc
    else:
        assert hasattr(module, name), \
               f"Object {name} not found in module {module_name}"


def test_channels_is_a_tinydb_instance():
    from brainslug import CHANNELS, ChannelStorage
    assert isinstance(CHANNELS, ChannelStorage)


def test_brain_is_a_query():
    from brainslug import Brain
    assert Query in Brain.__mro__
