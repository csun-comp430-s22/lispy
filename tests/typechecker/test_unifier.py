import pytest

from lispyc.typechecker import types
from lispyc.typechecker.unifier import Unifier


@pytest.fixture
def unifier():
    return Unifier()


def test_identical_unknowns_unify(unifier):
    unknown = types.UnknownType()

    unifier.unify(unknown, unknown)

    assert len(unifier._map) == 0


def test_unique_unknowns_unify(unifier):
    unknown_1 = types.UnknownType()
    unknown_2 = types.UnknownType()

    unifier.unify(unknown_1, unknown_2)

    representative_1 = unifier._get_transitive_set_representative(unknown_1)
    representative_2 = unifier._get_transitive_set_representative(unknown_2)

    assert representative_1 is representative_2
    assert (representative_1 is unknown_1) or (representative_2 is unknown_2)
