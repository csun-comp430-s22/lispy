import pytest

from lispyc import nodes
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

# TODO: should it be the typechecker's responsibility to disallow comparing functions?
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


@pytest.mark.parametrize(["program", "type_"], VALID_CONDS)
def test_cond_typechecks(program, type_):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]
