from unittest.mock import patch
from string import ascii_letters, digits
import inspect

from hypothesis import given, assume
from hypothesis import strategies as st
import pytest

from brainslug.ribosome import define, Symbol
from brainslug.remote import Remote


def test_remote_is_a_class():
    assert inspect.isclass(Remote)


def test_remote_needs_a_base_symbol():
    symbol = object()
    assert Remote(symbol).__symbol__ is symbol


def test_remote_may_contain_the_eval():
    eval = object()
    assert Remote(None, eval=eval).__eval__ is eval


def test_empty_attribute_is_not_valid():
    with pytest.raises(AttributeError):
        getattr(Remote(None), '')


@given(attribute=st.text())
def test_non_identifiers_are_invalid_attributes(attribute):
    assume(not attribute.isidentifier())
    with pytest.raises(AttributeError):
        getattr(Remote(None), attribute)


@given(path=st.lists(st.text(min_size=1,
                             alphabet=ascii_letters + digits + '_'),
                     min_size=1))
def test_attributes_are_other_remotes_if_ribosome_is_not_registered(path):
    assume(all(p.isidentifier()
               and not p.startswith('__')
               and not p.endswith('__')
               for p in path))

    with patch.dict("brainslug.ribosome.RIBOSOMES"):
        root = remote = Remote(Symbol())
        for part in path:
            remote = getattr(remote, part)

        assert isinstance(remote, Remote)
        assert remote is not root


@given(path=st.lists(st.text(min_size=1,
                             alphabet=ascii_letters + digits + '_'),
                     min_size=1))
def test_attributes_are_partial_if_ribosome_is_registered(path):
    assume(all(p.isidentifier()
               and not p.startswith('__')
               and not p.endswith('__')
               for p in path))

    called = False

    with patch.dict("brainslug.ribosome.RIBOSOMES"):
        root = remote = Remote(Symbol((path[0], )))

        @define(Symbol(path))
        def _(remote):
            nonlocal called
            called = True
            assert remote is root

        for part in path[1:]:
            remote = getattr(remote, part)

        remote()
        assert called


def test_call_pass_args_and_kwargs():
    args = (object(), object())
    kwargs = {'kw1': object(), 'kw2': object()}
    called = False

    with patch.dict("brainslug.ribosome.RIBOSOMES"):
        remote = Remote(Symbol())

        @define(Symbol())
        def _(remote, *c_args, **c_kwargs):
            nonlocal called
            called = True
            assert args == c_args
            assert kwargs == c_kwargs

        remote(*args, **kwargs)
        assert called


def test_call_returns_ribosome_return():
    result = object()

    with patch.dict("brainslug.ribosome.RIBOSOMES"):
        remote = Remote(Symbol())

        @define(Symbol())
        def _(remote, *c_args, **c_kwargs):
            return result

        assert remote() is result


def test_call_returns_ribosome_return():
    result = object()

    with patch.dict("brainslug.ribosome.RIBOSOMES"):
        remote = Remote(Symbol())

        @define(Symbol())
        def _(remote, *c_args, **c_kwargs):
            return result

        assert remote() is result


@pytest.mark.parametrize('special, convention, args',
                         [('__getitem__', 'getitem', (object(), )),
                          ('__setitem__', 'setitem', (object(), object())),
                          ('__delitem__', 'delitem', (object(), ))])
def test_special_ribosome_methods_are_reachable(special, convention, args):
    result = object()
    with patch.dict("brainslug.ribosome.RIBOSOMES"):
        remote = Remote(Symbol())

        @define(Symbol((convention, )))
        def _(remote, *c_args):
            assert c_args == args
            return result

        assert getattr(remote, special)(*args) is result
