from functools import reduce
from string import ascii_letters, digits
import inspect

from hypothesis import given, assume
from hypothesis import strategies as st
import pytest

from brainslug.ribosomes import Symbol


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


@given(path=st.tuples(st.text(min_size=1,
                              alphabet=ascii_letters + digits + '_')))
def test_symbol_is_aggregative(path):
    assume(not any(p[0] in digits for p in path))
    result = Symbol()
    for part in path:
        result = getattr(result, part)

    assert tuple(result) == path
