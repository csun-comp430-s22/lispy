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


@pytest.mark.parametrize("type_", [types.IntType, types.FloatType, types.BoolType])
def test_identical_basic_types_unify(unifier, type_):
    unifier.unify(type_(), type_())

    assert len(unifier._map) == 0


def test_unique_unknowns_unify(unifier):
    unknown_1 = types.UnknownType()
    unknown_2 = types.UnknownType()

    unifier.unify(unknown_1, unknown_2)

    representative_1 = unifier._get_transitive_set_representative(unknown_1)
    representative_2 = unifier._get_transitive_set_representative(unknown_2)

    assert representative_1 is representative_2
    assert (representative_1 is unknown_1) or (representative_2 is unknown_2)


def test_identical_lists_unify(unifier):
    list_1 = types.ListType(types.FloatType())
    list_2 = types.ListType(types.FloatType())

    unifier.unify(list_1, list_2)

    assert len(unifier._map) == 0


def test_identical_functions_unify(unifier):
    func_1 = types.FunctionType((types.IntType(), types.BoolType()), types.FloatType())
    func_2 = types.FunctionType((types.IntType(), types.BoolType()), types.FloatType())

    unifier.unify(func_1, func_2)

    assert len(unifier._map) == 0


def test_transitively_identical_functions_unify(unifier):
    param_1_unk = types.UnknownType()
    param_2_unk = types.UnknownType()
    return_unk = types.UnknownType()
    func_1_unk = types.UnknownType()

    func_1 = types.FunctionType((types.FloatType(), param_2_unk), types.BoolType())
    func_2 = types.FunctionType((param_1_unk, types.IntType()), return_unk)

    unifier.unify(func_1_unk, func_1)
    unifier.unify(func_1_unk, func_2)

    expected_func = types.FunctionType((types.FloatType(), types.IntType()), types.BoolType())

    assert expected_func == unifier._get_transitive_set_representative(func_1_unk)
    assert types.FloatType() == unifier._get_transitive_set_representative(param_1_unk)
    assert types.IntType() == unifier._get_transitive_set_representative(param_2_unk)
    assert types.BoolType() == unifier._get_transitive_set_representative(return_unk)
