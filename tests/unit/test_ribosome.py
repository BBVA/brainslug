from brainslug.ribosomes import define


def test_define_is_decorator():
    result = object()

    @define()
    def decorated():
        return result
    assert decorated() is result
