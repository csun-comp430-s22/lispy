import pytest

from lispyc import exceptions
from lispyc.nodes import BoolType, FloatType, FunctionType, IntType, ListType, Type
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

CONSTANTS = [
    ("120", IntType()),
    ("-40", IntType()),
    ("0", IntType()),
    ("12e35", FloatType()),
    ("-1e2", FloatType()),
    ("489e-29", FloatType()),
    ("true", BoolType()),
    ("false", BoolType()),
]

VALID_PROGNS = [
    ("(progn 1.0 2)", IntType()),
    ("(progn true 1.0)", FloatType()),
    ("(progn 1 false)", BoolType()),
    ("(progn (list 1.0 2.0) (list 1 2 3))", ListType(IntType())),
    ("(progn (lambda () true))", FunctionType((), BoolType())),
    ("(progn 1 1.0 true 2 false 3.0 true)", IntType()),
    ("(progn 1 (progn 2 2.0))", FloatType()),
    ("(progn false (progn 1 2) 3.0)", IntType()),
]

INVALID_PROGNS = [
    "(progn (list 1) (list 1 2.0 3))",
    "(progn 1 2 3.0 (car 7) 4.0 false)",
    "(progn 1.0 (progn true (list 2 3.0) 4) false)",
]


@pytest.mark.parametrize(["program", "type_"], CONSTANTS)
def test_constant_typechecks(program: str, type_: Type):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize(["program", "type_"], CONSTANTS)
def test_progn_typechecks(program: str, type_: Type):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_PROGNS)
def test_invalid_form_in_progn_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)
