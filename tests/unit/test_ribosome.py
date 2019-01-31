import pytest
from unittest.mock import patch

from brainslug import ribosome
from brainslug.ribosome import define


def test_define_is_decorator():
    with patch.dict("brainslug.ribosome.RIBOSOMES"):
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
    with patch.dict("brainslug.ribosome.RIBOSOMES"):
        symbol = tuple()

        @define(symbol)
        def decorated():
            pass

        assert symbol in ribosome.RIBOSOMES
        assert ribosome.RIBOSOMES[symbol] is decorated


def test_define_cant_register_ribosome_twice():
    with patch.dict("brainslug.ribosome.RIBOSOMES"):
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
