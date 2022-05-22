import pytest

from lispyc import exceptions, nodes
from lispyc.nodes import ListType
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

VALID_LISTS = [
    ("(list 1 2 3)", ListType(nodes.IntType())),
    ("(list 12.1 7e-1 -2.2)", ListType(nodes.FloatType())),
    ("(list true false true true true)", ListType(nodes.BoolType())),
    (
        "(list (lambda ((x int) (y float)) 2) (lambda ((a int) (b float)) 5))",
        ListType(nodes.FunctionType((nodes.IntType(), nodes.FloatType()), nodes.IntType())),
    ),
    ("(list (list 1 2) (list 3))", ListType(ListType(nodes.IntType()))),
    ("(list (list false true) () (list true))", ListType(ListType(nodes.BoolType()))),
    ("(list () (list (list 3e-1) ()))", ListType(ListType(ListType(nodes.FloatType())))),
]

INVALID_LISTS = [
    "(list 1 false)",
    "(list true 7 () 1.3)",
    "(list 7e-1 1)",
    "(list 12 (lambda ((c float)) 8))",
    "(list (list 3) 4)",
    "(list 12.4 89.2 (list false))",
    "(list (list 8 9 10) (list 3 4 5) (list false))",
    "(list (list 1.2 3.4) (list 7.8 9.1) (list (list 3.2) (list 3.3)))",
    "(list (lambda ((x int) (y int)) 2) (lambda ((a int) (b float)) 5))",
    "(list (lambda ((x int)) 2) (lambda ((a int) (b float)) 5))",
    "(list (lambda () 1) (lambda () 1.0))",
]

VALID_CONS = [
    ("(cons 1 (list 2))", ListType(nodes.IntType())),
    ("(cons 3.7 (list 3e-2 5.2))", ListType(nodes.FloatType())),
    ("(cons false (list true false false true))", ListType(nodes.BoolType())),
    ("(cons (list 1 2 3) (list (list 4) (list 5 6)))", ListType(ListType(nodes.IntType()))),
    ("(cons 1 ())", ListType(nodes.IntType())),
    ("(cons 4.73 ())", ListType(nodes.FloatType())),
    ("(cons false ())", ListType(nodes.BoolType())),
    ("(cons (list 7) ())", ListType(ListType(nodes.IntType()))),
    ("(cons () (list (list false)))", ListType(ListType(nodes.BoolType()))),  # TODO: disallow?
    (
        "(cons (cons 1.5 (list 7.9 2.3 7.7)) (list (list 2.2) (list 1.1)))",
        ListType(ListType(nodes.FloatType())),
    ),
    ("(cons 7 (cons 8 (list 9)))", ListType(nodes.IntType())),
]

INVALID_CONS = [
    "(cons 1 2)",
    "(cons 7.9 2.2)",
    "(cons true false)",
    "(cons (lambda () 2) (lambda () 1))",
    "(cons 1 (list 3.4))",
    "(cons (list false) true)",
    "(cons (list 1.1) (list 2.3 4.4))",
    "(cons () (list 12))",
    "(cons (lambda ((x int) (y int)) 2) (list (lambda ((a int) (b float)) 5)))",
    "(cons (lambda ((x int)) 2) (list (lambda ((a int) (b float)) 5)))",
    "(cons (lambda () 1) (list (lambda () 1.0)))",
]

VALID_CARS = [
    ("(car (list 1 2))", nodes.IntType()),
    ("(car (list 7.6 1.2 3.4))", nodes.FloatType()),
    ("(car (list true false true))", nodes.BoolType()),
    ("(car (list (lambda () 1) (lambda () 2)))", nodes.FunctionType((), nodes.IntType())),
    ("(car (list (list 7 8) (list 9)))", ListType(nodes.IntType())),
    ("(car (list () (list 1.2 3e-2)))", ListType(nodes.FloatType())),
    ("(car (car (list (list false))))", nodes.BoolType()),
    ("(car (cdr (list 1.2 3e4)))", nodes.FloatType()),
    ("(car (cons 1 (list 2 3)))", nodes.IntType()),
]

INVALID_CARS = [
    "(car 1)",
    "(car -9e2)",
    "(car false)",
    "(car (car (list 7 8)))",
    "(car (lambda () 1))",
]

VALID_CDRS = [
    ("(cdr (list 1 2))", ListType(nodes.IntType())),
    ("(cdr (list 7.6 1.2 3.4))", ListType(nodes.FloatType())),
    ("(cdr (list true false true))", ListType(nodes.BoolType())),
    ("(cdr (list (lambda () 1) (lambda () 2)))", ListType(nodes.FunctionType((), nodes.IntType()))),
    ("(cdr (list (list 7 8) (list 9)))", ListType(ListType(nodes.IntType()))),
    ("(cdr (list () (list 1.2 3e-2)))", ListType(ListType(nodes.FloatType()))),
    ("(cdr (car (list (list false))))", ListType(nodes.BoolType())),
    ("(cdr (cdr (list (list 7.9) (list -1e2 3.4))))", ListType(ListType(nodes.FloatType()))),
    ("(cdr (cons 1 (list 2 3)))", ListType(nodes.IntType())),
]

INVALID_CDRS = [
    "(cdr 1)",
    "(cdr -9e2)",
    "(cdr false)",
    "(cdr (car (list 1.2 3.4 5.6)))",
    "(cdr (lambda () 1))",
]


@pytest.mark.parametrize("program", ["(list)", "()"])
def test_nil_typechecks(program: str):
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
def test_list_typechecks(program: str, type_: ListType):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_LISTS)
def test_invalid_list_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize(["program", "type_"], VALID_CONS)
def test_cons_typechecks(program: str, type_: nodes.ListType):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


def test_cons_nil_typechecks():
    program_node = parse("(cons () ())")  # TODO: should this even be allowed?
    [result] = list(TypeChecker.check_program(program_node))

    assert isinstance(result, ListType)
    assert isinstance(result.element_type, ListType)
    assert isinstance(result.element_type.element_type, nodes.UnknownType)


@pytest.mark.parametrize("program", INVALID_CONS)
def test_invalid_cons_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.UnificationError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize(["program", "type_"], VALID_CARS)
def test_cars_typechecks(program: str, type_: nodes.Type):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_CARS)
def test_invalid_cars_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize(["program", "type_"], VALID_CDRS)
def test_cdrs_typechecks(program: str, type_: nodes.ListType):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_CDRS)
def test_invalid_cdrs_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)
