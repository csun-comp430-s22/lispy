from itertools import combinations

import pytest

from lispyc.typechecker import types
from lispyc.typechecker.unifier import Unifier

BASIC_TYPES = [types.IntType, types.FloatType, types.BoolType]
BASIC_TYPE_PAIRS = list(combinations(BASIC_TYPES, r=2))

DIFFERENT_FUNCTION_TYPES = [
    (
        types.FunctionType((types.FloatType(),), types.BoolType()),
        types.FunctionType((types.IntType(),), types.BoolType()),
    ),
    (
        types.FunctionType((types.FloatType(),), types.BoolType()),
        types.FunctionType((types.FloatType(),), types.IntType()),
    ),
    (
        types.FunctionType((types.IntType(),), types.BoolType()),
        types.FunctionType((types.FloatType(),), types.IntType()),
    ),
    (
        types.FunctionType((types.BoolType(), types.FloatType()), types.IntType()),
        types.FunctionType((types.FloatType(), types.BoolType()), types.IntType()),
    ),
]

DIFFERENT_PARAM_COUNTS = [
    (
        types.FunctionType((), types.BoolType()),
        types.FunctionType((types.BoolType(),), types.BoolType()),
    ),
    (
        types.FunctionType((types.FloatType(), types.IntType()), types.BoolType()),
        types.FunctionType((types.FloatType(),), types.BoolType()),
    ),
    (
        types.FunctionType((types.BoolType(), types.IntType(), types.BoolType()), types.BoolType()),
        types.FunctionType((types.IntType(),), types.BoolType()),
    ),
    (
        # Different types too.
        types.FunctionType((types.BoolType(), types.IntType()), types.FloatType()),
        types.FunctionType((types.IntType(),), types.IntType()),
    ),
]


@pytest.fixture
def unifier():
    return Unifier()


def test_identical_unknowns_unify(unifier):
    unknown = types.UnknownType()

    unifier.unify(unknown, unknown)

    assert len(unifier._map) == 0


@pytest.mark.parametrize("type_", BASIC_TYPES)
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


@pytest.mark.parametrize("type_", BASIC_TYPES)
def test_transitively_identical_basic_types_unify(unifier, type_):
    unifier.unify(type_(), type_())


def test_transitively_identical_lists_unify(unifier):
    element_1 = types.UnknownType()
    element_2 = types.UnknownType()
    list_unk = types.UnknownType()

    list_1 = types.ListType(element_1)
    list_2 = types.ListType(element_2)

    unifier.unify(types.BoolType(), element_2)
    unifier.unify(list_1, list_unk)
    unifier.unify(list_2, list_unk)

    assert types.ListType(types.BoolType()) == unifier._get_transitive_set_representative(list_unk)
    assert types.BoolType() == unifier._get_transitive_set_representative(element_1)
    assert types.BoolType() == unifier._get_transitive_set_representative(element_2)


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


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_different_basic_types_fail(unifier, left, right):
    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(left(), right())


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_different_lists_fail(unifier, left, right):
    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(types.ListType(left()), types.ListType(right()))


@pytest.mark.parametrize(["left", "right"], DIFFERENT_FUNCTION_TYPES)
def test_different_function_types_fail(unifier, left, right):
    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(left, right)


@pytest.mark.parametrize(["left", "right"], DIFFERENT_PARAM_COUNTS)
def test_different_param_counts_fail(unifier, left, right):
    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(left, right)


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_transitively_different_basic_types_fail(unifier, left, right):
    left_unk = types.UnknownType()
    right_unk = types.UnknownType()

    unifier.unify(left_unk, left())
    unifier.unify(right_unk, right())

    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(left_unk, right_unk)


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_transitively_different_lists_fail(unifier, left, right):
    element_1 = types.UnknownType()
    element_2 = types.UnknownType()
    list_unk = types.UnknownType()

    list_1 = types.ListType(element_1)
    list_2 = types.ListType(element_2)

    unifier.unify(element_1, left())
    unifier.unify(element_2, right())
    unifier.unify(list_1, list_unk)

    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(list_2, list_unk)


def test_transitively_different_function_params_fail(unifier):
    param_1_unk = types.UnknownType()
    param_2_unk = types.UnknownType()
    func_1_unk = types.UnknownType()

    func_1 = types.FunctionType((types.FloatType(), param_2_unk), types.BoolType())
    func_2 = types.FunctionType((param_1_unk, types.IntType()), types.BoolType())

    unifier.unify(param_1_unk, types.BoolType())
    unifier.unify(param_2_unk, types.FloatType())
    unifier.unify(func_1_unk, func_1)

    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(func_1_unk, func_2)


def test_transitively_different_function_returns_fail(unifier):
    return_unk = types.UnknownType()
    func_1_unk = types.UnknownType()

    func_1 = types.FunctionType((types.FloatType(), types.IntType()), types.BoolType())
    func_2 = types.FunctionType((types.FloatType(), types.IntType()), return_unk)

    unifier.unify(return_unk, types.IntType())
    unifier.unify(func_1_unk, func_1)

    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(func_1_unk, func_2)


def test_cyclic_list_fails(unifier):
    unknown = types.UnknownType()
    list_ = types.ListType(unknown)

    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(unknown, list_)


def test_cyclic_function_param_fails(unifier):
    unknown = types.UnknownType()
    func = types.FunctionType((unknown,), types.BoolType())

    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(unknown, func)


def test_cyclic_function_return_fails(unifier):
    unknown = types.UnknownType()
    func = types.FunctionType((types.BoolType(),), unknown)

    with pytest.raises(ValueError):  # noqa: PT011 TODO: Use custom exception type.
        unifier.unify(unknown, func)