import pytest
from unittest.mock import patch

from brainslug import ribosomes
from brainslug.ribosomes import define


def test_define_is_decorator():
    with patch.dict("brainslug.ribosomes.RIBOSOMES"):
        result = object()

        @define(tuple())
        def decorated():
            return result
        assert decorated() is result


def test_define_needs_symbol():
    with pytest.raises(TypeError):
        @define()
        def decorated():
            pass


def test_define_registers_ribosome():
    with patch.dict("brainslug.ribosomes.RIBOSOMES"):
        symbol = tuple()

        @define(symbol)
        def decorated():
            pass

        assert symbol in ribosomes.RIBOSOMES
        assert ribosomes.RIBOSOMES[symbol] is decorated


def test_define_cant_register_ribosome_twice():
    with patch.dict("brainslug.ribosomes.RIBOSOMES"):
        symbol = tuple()

        @define(symbol)
        def decorated():
            pass

        with pytest.raises(ValueError):
            @define(symbol)
            def other_decorated():
                pass


def test_define_cant_register_dunder_symbols():
    symbol = ("__str__", )

    with pytest.raises(ValueError):
        @define(symbol)
        def other_decorated():
            pass
