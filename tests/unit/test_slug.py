import inspect

from brainslug import Slug


def test_slug_is_a_class():
    assert inspect.isclass(Slug)


def test_slug_stores_attributes():
    fn = object()
    spec = object()
    slug = Slug(fn, spec)
    assert slug.fn is fn
    assert slug.spec is spec
