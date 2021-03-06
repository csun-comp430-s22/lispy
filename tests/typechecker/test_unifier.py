from itertools import combinations

import pytest

from lispyc.exceptions import CyclicTypeError, UnificationError
from lispyc.nodes import BoolType, FloatType, FunctionType, IntType, ListType, Type, UnknownType
from lispyc.typechecker import Unifier

BASIC_TYPES = [IntType, FloatType, BoolType]
BASIC_TYPE_PAIRS = list(combinations(BASIC_TYPES, r=2))

DIFFERENT_FUNCTION_TYPES = [
    (
        FunctionType((FloatType(),), BoolType()),
        FunctionType((IntType(),), BoolType()),
    ),
    (
        FunctionType((FloatType(),), BoolType()),
        FunctionType((FloatType(),), IntType()),
    ),
    (
        FunctionType((IntType(),), BoolType()),
        FunctionType((FloatType(),), IntType()),
    ),
    (
        FunctionType((BoolType(), FloatType()), IntType()),
        FunctionType((FloatType(), BoolType()), IntType()),
    ),
]

DIFFERENT_PARAM_COUNTS = [
    (
        FunctionType((), BoolType()),
        FunctionType((BoolType(),), BoolType()),
    ),
    (
        FunctionType((FloatType(), IntType()), BoolType()),
        FunctionType((FloatType(),), BoolType()),
    ),
    (
        FunctionType((BoolType(), IntType(), BoolType()), BoolType()),
        FunctionType((IntType(),), BoolType()),
    ),
    (
        # Different types too.
        FunctionType((BoolType(), IntType()), FloatType()),
        FunctionType((IntType(),), IntType()),
    ),
]


@pytest.fixture
def unifier() -> Unifier:
    return Unifier()


def test_identical_unknowns_unify(unifier: Unifier):
    unknown = UnknownType()

    unifier.unify(unknown, unknown)

    assert len(unifier._map) == 0  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize("type_", BASIC_TYPES)
def test_identical_basic_types_unify(unifier: Unifier, type_: type[Type]):
    unifier.unify(type_(), type_())

    assert len(unifier._map) == 0  # pyright: ignore[reportPrivateUsage]


def test_unique_unknowns_unify(unifier: Unifier):
    unknown_1 = UnknownType()
    unknown_2 = UnknownType()

    unifier.unify(unknown_1, unknown_2)

    representative_1 = unifier.get_transitive_set_representative(unknown_1)
    representative_2 = unifier.get_transitive_set_representative(unknown_2)

    assert representative_1 is representative_2
    assert (representative_1 is unknown_1) or (representative_2 is unknown_2)


def test_identical_lists_unify(unifier: Unifier):
    list_1 = ListType(FloatType())
    list_2 = ListType(FloatType())

    unifier.unify(list_1, list_2)

    assert len(unifier._map) == 0  # pyright: ignore[reportPrivateUsage]


def test_identical_functions_unify(unifier: Unifier):
    func_1 = FunctionType((IntType(), BoolType()), FloatType())
    func_2 = FunctionType((IntType(), BoolType()), FloatType())

    unifier.unify(func_1, func_2)

    assert len(unifier._map) == 0  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize("type_", BASIC_TYPES)
def test_transitively_identical_basic_types_unify(unifier: Unifier, type_: type[Type]):
    unifier.unify(type_(), type_())


def test_transitively_identical_lists_unify(unifier: Unifier):
    element_1 = UnknownType()
    element_2 = UnknownType()
    list_unk = UnknownType()

    list_1 = ListType(element_1)
    list_2 = ListType(element_2)

    unifier.unify(BoolType(), element_2)
    unifier.unify(list_1, list_unk)
    unifier.unify(list_2, list_unk)

    assert ListType(BoolType()) == unifier.get_transitive_set_representative(list_unk)
    assert BoolType() == unifier.get_transitive_set_representative(element_1)
    assert BoolType() == unifier.get_transitive_set_representative(element_2)


def test_transitively_identical_functions_unify(unifier: Unifier):
    param_1_unk = UnknownType()
    param_2_unk = UnknownType()
    return_unk = UnknownType()
    func_1_unk = UnknownType()

    func_1 = FunctionType((FloatType(), param_2_unk), BoolType())
    func_2 = FunctionType((param_1_unk, IntType()), return_unk)

    unifier.unify(func_1_unk, func_1)
    unifier.unify(func_1_unk, func_2)

    expected_func = FunctionType((FloatType(), IntType()), BoolType())

    assert expected_func == unifier.get_transitive_set_representative(func_1_unk)
    assert FloatType() == unifier.get_transitive_set_representative(param_1_unk)
    assert IntType() == unifier.get_transitive_set_representative(param_2_unk)
    assert BoolType() == unifier.get_transitive_set_representative(return_unk)


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_different_basic_types_fail(unifier: Unifier, left: type[Type], right: type[Type]):
    with pytest.raises(UnificationError):
        unifier.unify(left(), right())


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_different_lists_fail(unifier: Unifier, left: type[Type], right: type[Type]):
    with pytest.raises(UnificationError):
        unifier.unify(ListType(left()), ListType(right()))


@pytest.mark.parametrize(["left", "right"], DIFFERENT_FUNCTION_TYPES)
def test_different_function_types_fail(unifier: Unifier, left: FunctionType, right: FunctionType):
    with pytest.raises(UnificationError):
        unifier.unify(left, right)


@pytest.mark.parametrize(["left", "right"], DIFFERENT_PARAM_COUNTS)
def test_different_param_counts_fail(unifier: Unifier, left: FunctionType, right: FunctionType):
    with pytest.raises(UnificationError):
        unifier.unify(left, right)


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_transitively_different_basic_types_fail(
    unifier: Unifier, left: type[Type], right: type[Type]
):
    left_unk = UnknownType()
    right_unk = UnknownType()

    unifier.unify(left_unk, left())
    unifier.unify(right_unk, right())

    with pytest.raises(UnificationError):
        unifier.unify(left_unk, right_unk)


@pytest.mark.parametrize(["left", "right"], BASIC_TYPE_PAIRS)
def test_transitively_different_lists_fail(unifier: Unifier, left: type[Type], right: type[Type]):
    element_1 = UnknownType()
    element_2 = UnknownType()
    list_unk = UnknownType()

    list_1 = ListType(element_1)
    list_2 = ListType(element_2)

    unifier.unify(element_1, left())
    unifier.unify(element_2, right())
    unifier.unify(list_1, list_unk)

    with pytest.raises(UnificationError):
        unifier.unify(list_2, list_unk)


def test_transitively_different_function_params_fail(unifier: Unifier):
    param_1_unk = UnknownType()
    param_2_unk = UnknownType()
    func_1_unk = UnknownType()

    func_1 = FunctionType((FloatType(), param_2_unk), BoolType())
    func_2 = FunctionType((param_1_unk, IntType()), BoolType())

    unifier.unify(param_1_unk, BoolType())
    unifier.unify(param_2_unk, FloatType())
    unifier.unify(func_1_unk, func_1)

    with pytest.raises(UnificationError):
        unifier.unify(func_1_unk, func_2)


def test_transitively_different_function_returns_fail(unifier: Unifier):
    return_unk = UnknownType()
    func_1_unk = UnknownType()

    func_1 = FunctionType((FloatType(), IntType()), BoolType())
    func_2 = FunctionType((FloatType(), IntType()), return_unk)

    unifier.unify(return_unk, IntType())
    unifier.unify(func_1_unk, func_1)

    with pytest.raises(UnificationError):
        unifier.unify(func_1_unk, func_2)


def test_cyclic_list_fails(unifier: Unifier):
    unknown = UnknownType()
    list_ = ListType(unknown)

    with pytest.raises(CyclicTypeError):
        unifier.unify(unknown, list_)


def test_cyclic_function_param_fails(unifier: Unifier):
    unknown = UnknownType()
    func = FunctionType((unknown,), BoolType())

    with pytest.raises(CyclicTypeError):
        unifier.unify(unknown, func)


def test_cyclic_function_return_fails(unifier: Unifier):
    unknown = UnknownType()
    func = FunctionType((BoolType(),), unknown)

    with pytest.raises(CyclicTypeError):
        unifier.unify(unknown, func)
