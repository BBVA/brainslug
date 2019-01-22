import importlib
from tinydb import TinyDB
import pytest


@pytest.mark.parametrize('module_name, name',
                         [('brainslug', 'Channel'),
                          ('brainslug', 'CHANNELS'),
                          ('brainslug.utils', 'SyncedVar'),
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
    from brainslug import CHANNELS
    assert isinstance(CHANNELS, TinyDB)
