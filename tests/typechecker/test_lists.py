import pytest

from lispyc import exceptions, nodes
from lispyc.nodes import ListType
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

VALID_LISTS = [
    ("(list 1 2 3)", ListType(nodes.IntType())),
    ("(list 12.1 7e-1 -2.2)", ListType(nodes.FloatType())),
    ("(list true false true true true)", ListType(nodes.BoolType())),
    ("(list (list 1 2) (list 3))", ListType(ListType(nodes.IntType()))),
    ("(list (list false true) () (list true))", ListType(ListType(nodes.BoolType()))),
    ("(list () (list (list 3e-1) ()))", ListType(ListType(ListType(nodes.FloatType())))),
]

INVALID_LISTS = [
    "(list 1 false)",
    "(list true 7 () 1.3)",
    "(list 7e-1 1)",
    "(list (list 3) 4)",
    "(list 12.4 89.2 (list false))",
    "(list (list 8 9 10) (list 3 4 5) (list false))",
    "(list (list 1.2 3.4) (list 7.8 9.1) (list (list 3.2) (list 3.3)))",
]


@pytest.mark.parametrize("program", ["(list)", "()"])
def test_nil_typechecks(program):
    program_node = parse(program)
    [result] = list(TypeChecker.check_program(program_node))

    assert isinstance(result, ListType)
    assert isinstance(result.element_type, nodes.UnknownType)


def test_nested_nil_typechecks():
    program_node = parse("(list () (list () ()) ())")
    [result] = list(TypeChecker.check_program(program_node))

    assert isinstance(result, ListType)
    assert isinstance(result.element_type, ListType)
    assert isinstance(result.element_type.element_type, ListType)
    assert isinstance(result.element_type.element_type.element_type, nodes.UnknownType)


@pytest.mark.parametrize(["program", "type_"], VALID_LISTS)
def test_list_typechecks(program, type_):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_LISTS)
def test_invalid_list_type_error(program):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)
