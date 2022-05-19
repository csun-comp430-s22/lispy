import pytest

from lispyc import exceptions, nodes
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

VALID_CONDS = [
    ("(cond (true 7) (false -1) (true 100) (false 15) 9)", nodes.IntType()),
    ("(cond (false 3.7) (true 9e-1) 14.03)", nodes.FloatType()),
    ("(cond (false false) (false true) (true true) true)", nodes.BoolType()),
    ("(cond (true (list 1 2)) (true (list 3 4)) ())", nodes.ListType(nodes.IntType())),
    ("(cond (false (cond (true 99) (false 77) 1)) (true 2) 3)", nodes.IntType()),
    ("(cond (true 3.1) (false -19e1) (cond (false -55.6) 92.1))", nodes.FloatType()),
    ("(cond ((cond (true false) true) 1) (false 2) 0)", nodes.IntType()),
    ("(cond (true (select 1 (2 99.9) 82.1)) (false 3e-1) 47.12)", nodes.FloatType()),
]

VALID_SELECTS = [
    ("(select 0.2 (1.1 7) (2.4 -1) (3.9 100) (4.1 15) 9)", nodes.IntType()),
    ("(select 11 (22 3.7) (33 9e-1) 14.03)", nodes.FloatType()),
    ("(select true (false false) (false true) (true true) true)", nodes.BoolType()),
    ("(select (list 0) (() (list 1 2)) ((list 7) (list 3 4)) ())", nodes.ListType(nodes.IntType())),
    ("(select 1 (1 (select false (true 99) (false 77) 1)) (3 2) 3)", nodes.IntType()),
    ("(select (select 1 (1 90) 80) (22 -19e1) (select 5 (6 -55.6) 92.1))", nodes.FloatType()),
    ("(select false ((select false (true false) true) 1) (false 2) 0)", nodes.IntType()),
    ("(select 4.3 (9.1 (cond (true 99.9) 82.1)) (4.3 3e-1) 47.12)", nodes.FloatType()),
]

INVALID_CONDS = [
    "(cond (true 1) (7 2) (false 3) 4)",
    "(cond (12.3 true) (14.3 true) (9.1 false) true)",
    "(cond (true 1) (true 9.2) 2)",
    "(cond (2 6) (false 1) (7.3 true) 8.4)",
]

INVALID_SELECTS = [
    "(select 2.1 (true 1) (7 2) (false 3) 4)",
    "(select false (12.3 true) (14.3 true) (9.1 false) true)",
    "(select 1 (1 1) (2 9.2) 2)",
    "(select 1.1 (2.2 0) (2.3 1) false)",
]


@pytest.mark.parametrize(["program", "type_"], VALID_CONDS)
def test_cond_typechecks(program, type_):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_CONDS)
def test_invalid_cond_type_error(program):
    program_node = parse(program)

    with pytest.raises(exceptions.UnificationError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize(["program", "type_"], VALID_SELECTS)
def test_select_typechecks(program, type_):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_SELECTS)
def test_invalid_select_type_error(program):
    program_node = parse(program)

    with pytest.raises(exceptions.UnificationError):
        TypeChecker.check_program(program_node)
