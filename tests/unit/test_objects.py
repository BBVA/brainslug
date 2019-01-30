import importlib
from tinydb import TinyDB, Query
import pytest


@pytest.mark.parametrize('module_name, name',
                         [('brainslug', 'Brain'),
                          ('brainslug.channel', 'Channel'),
                          ('brainslug.channel', 'CHANNELS'),
                          ('brainslug.channel', 'ChannelStorage'),
                          ('brainslug.channel', 'SyncedVar'),
                          ('brainslug.ribosomes', 'RIBOSOMES'),
                          ('brainslug._slug', 'run_slug'),
                          ('brainslug._slug', 'Slug'),
                          ('brainslug.util', 'get_resources'),
                          ('brainslug.util', 'to_remote'),
                          ('brainslug.util', 'wait_for_resources'),
                          ('brainslug.webapp', 'config_routes'),
                          ('brainslug.webapp', 'process_agent_request'),
                          ('brainslug.webapp', 'run_web_server')])
def test_object_is_importable(module_name, name):
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        assert False, exc
    else:
        assert hasattr(module, name), \
               f"Object {name} not found in module {module_name}"


def test_channels_is_a_tinydb_instance():
    from brainslug.channel import CHANNELS, ChannelStorage
    assert isinstance(CHANNELS, ChannelStorage)


def test_brain_is_a_query():
    from brainslug import Brain
    assert Query in Brain.__mro__
