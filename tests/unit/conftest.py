import pytest


@pytest.fixture
def session():
    from brainslug import Session
    return Session(None, None, None)
