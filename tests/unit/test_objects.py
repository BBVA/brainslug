import importlib
from tinydb import TinyDB, Query
import pytest


@pytest.mark.parametrize('module_name, name',
                         [('brainslug', 'Channel'),
                          ('brainslug', 'CHANNELS'),
                          ('brainslug.utils', 'SyncedVar'),
                          ('brainslug', 'Slug'),
                          ('brainslug', 'Brain'),
                          ])
def test_object_is_importable(module_name, name):
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        assert False, exc
    else:
        assert hasattr(module, name), \
               f"Object {name} not found in module {module_name}"


def test_channels_is_a_tinydb_instance():
    from brainslug import CHANNELS
    assert isinstance(CHANNELS, TinyDB)


def test_brain_is_a_query():
    from brainslug import Brain
    assert Query in Brain.__mro__
