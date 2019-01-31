from functools import reduce
from string import ascii_letters, digits
import inspect

from hypothesis import given, assume
from hypothesis import strategies as st
import pytest

from brainslug.ribosome import Symbol


def test_symbol_is_a_class():
    assert inspect.isclass(Symbol)


def test_symbol_is_tuple_subclass():
    assert issubclass(Symbol, tuple)


def test_symbol_empty_attribute():
    with pytest.raises(AttributeError):
        getattr(Symbol(), '')


@given(attribute=st.text())
def test_symbol_invalid_attribute(attribute):
    assume(not attribute.isidentifier())
    with pytest.raises(AttributeError):
        getattr(Symbol(), attribute)


@given(path=st.lists(st.text(min_size=1,
                             alphabet=ascii_letters + digits + '_'),
                     min_size=1))
def test_symbol_is_aggregative(path):
    assume(not any(p[0] in digits
                   or (p.startswith('__') and p.endswith('__'))
                   for p in path))
    result = Symbol()
    for part in path:
        result = getattr(result, part)

    assert tuple(result) == tuple(path)
