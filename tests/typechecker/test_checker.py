import pytest

from lispyc import nodes
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

CONSTANTS = [
    ("120", nodes.IntType()),
    ("-40", nodes.IntType()),
    ("0", nodes.IntType()),
    ("12e35", nodes.FloatType()),
    ("-1e2", nodes.FloatType()),
    ("489e-29", nodes.FloatType()),
    ("true", nodes.BoolType()),
    ("false", nodes.BoolType()),
]


@pytest.mark.parametrize(["program", "type_"], CONSTANTS)
def test_constant_typechecks(program: str, type_: nodes.Type):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]
