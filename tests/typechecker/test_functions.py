import pytest

from lispyc import exceptions
from lispyc.nodes import BoolType, FloatType, FunctionType, IntType, ListType, SpecialForm
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

VALID_LAMBDAS = [
    ("(lambda () 1)", FunctionType((), IntType())),
    ("(lambda () 1.0)", FunctionType((), FloatType())),
    ("(lambda () false)", FunctionType((), BoolType())),
    ("(lambda () (lambda () 1))", FunctionType((), FunctionType((), IntType()))),
    (
        "(lambda ((x int) (y float) (z bool)) (list 1 2 3))",
        FunctionType((IntType(), FloatType(), BoolType()), ListType(IntType())),
    ),
    (
        "(lambda ((y float)) (lambda ((z int)) 12))",
        FunctionType((FloatType(),), FunctionType((IntType(),), IntType())),
    ),
    (
        "(lambda ((a int)) (lambda ((a float)) true))",
        FunctionType((IntType(),), FunctionType((FloatType(),), BoolType())),
    ),
    (
        "(lambda ((a (list int)) (b (list float)) (c (list bool))) 7e1)",
        FunctionType(
            (ListType(IntType()), ListType(FloatType()), ListType(BoolType())), FloatType()
        ),
    ),
    (
        "(lambda ((l (list (list int)))) (list false))",
        FunctionType((ListType(ListType(IntType())),), ListType(BoolType())),
    ),
    (
        "(lambda ((f (func (int float bool) float))) 1.1)",
        FunctionType(
            (FunctionType((IntType(), FloatType(), BoolType()), FloatType()),), FloatType()
        ),
    ),
    (
        "(lambda ((f (func ((list (list bool))) (list float)))) 1)",
        FunctionType(
            (FunctionType((ListType(ListType(BoolType())),), ListType(FloatType())),), IntType()
        ),
    ),
    (
        "(lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float))) "
        "(g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9))))",
        FunctionType(
            (FunctionType((FloatType(),), FloatType()),),
            FunctionType(
                (
                    FunctionType((), FunctionType((IntType(),), FloatType())),
                    FunctionType((BoolType(), IntType()), ListType(BoolType())),
                    ListType(IntType()),
                ),
                ListType(FunctionType((), FloatType())),
            ),
        ),
    ),
]

VALID_COMPOSED_FORMS = [
    ("((lambda () 1))", IntType()),
    ("((lambda () 1.0))", FloatType()),
    ("((lambda () false))", BoolType()),
    ("((lambda () (lambda () 1)))", FunctionType((), IntType())),
    ("((lambda ((x int) (y float) (z bool)) (list 1 2 3)) 1 2.0 false)", ListType(IntType())),
    (
        "((lambda ((y float)) (lambda ((z int)) 12)) 1.0)",
        FunctionType((IntType(),), IntType()),
    ),
    (
        "((lambda ((a int)) (lambda ((a float)) true)) 1)",
        FunctionType((FloatType(),), BoolType()),
    ),
    (
        "((lambda ((a (list int)) (b (list float)) (c (list bool))) 7e1) "
        "(list 1 2 3 4 -5) (list 2e-1 3.0) (list false))",
        FloatType(),
    ),
    (
        "((lambda ((l (list (list int)))) (list false)) (list (list 1) (list 2 3 4)))",
        ListType(BoolType()),
    ),
    (
        "((lambda ((f (func (int float bool) float))) 1.1) "
        "(lambda ((a int) (b float) (c bool)) 2.2))",
        FloatType(),
    ),
    (
        "((lambda ((f (func ((list (list bool))) (list float)))) 1) "
        "(lambda ((l (list (list bool)))) (list 1.2 3.4)))",
        IntType(),
    ),
    (
        "((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float))) "
        "(g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9)))) "
        "(lambda ((a float)) 9e-1))",
        FunctionType(
            (
                FunctionType((), FunctionType((IntType(),), FloatType())),
                FunctionType((BoolType(), IntType()), ListType(BoolType())),
                ListType(IntType()),
            ),
            ListType(FunctionType((), FloatType())),
        ),
    ),
    (
        "(((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float))) "
        "(g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9)))) "
        "(lambda ((a float)) 9e-1))"
        "(lambda () (lambda ((a int)) 1.2)) (lambda ((a bool) (b int)) (list true)) (list 1 2 3))",
        ListType(FunctionType((), FloatType())),
    ),
]

VALUES = ["1", "1e-2", "false", "(list 1 2 3)", "(lambda ((j int) (k float)) 13)"]

INVALID_LAMBDA_BODIES = [
    "(lambda ((x int)) (list 7 1.2))",
    "(lambda () (lambda ((b bool) (c int)) (car 99)))",
]

INVALID_NAME_LAMBDAS = [
    "(lambda (({name} float)) {return_val})",
    "(lambda (({name} (list int))) {return_val})",
    "(lambda (({name} (func (int) float))) {return_val})",
    "(lambda (({name} int) ({name} float)) {return_val})",
    "(lambda ((y int) ({name} bool) (x float)) {return_val})",
    "(lambda () (lambda (({name} float)) {return_val}))",
]

DUPLICATE_NAME_LAMBDAS = [
    "(lambda ((x int) (x int)) {return_val})",
    "(lambda ((x bool) (y int) (x bool)) {return_val})",
    "(lambda ((z_Y int) (z_Y float)) {return_val})",
    "(lambda ((j int) (j float)) {return_val})",
    "(lambda () (lambda ((b float) (b int)) {return_val}))",
]

MISSING_ARGS_COMPOSED_FORMS = [
    "((lambda ((x int) (y float) (z bool)) (list 1 2 3)) 1 2.3)",
    "((lambda ((f (func (int float bool) float))) 1.1))",
    "((lambda ((f (func ((list (list bool))) (list float)))) 1))",
    """
    (((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float)))
    (g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9)))))
    (lambda () (lambda ((a int)) 1.2)) (lambda ((a bool) (b int)) (list true)) (list 1 2))
    """,
    """
    (((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float)))
    (g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9))))
    (lambda ((a float)) 9e-1))
    (lambda () (lambda ((a int)) 1.2)) (lambda ((a bool) (b int)) (list true)))
    """,
    """
    (((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float)))
    (g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9))))
    (lambda ((a float)) 9e-1))
    (lambda () (lambda ((a int)) 1.2)) (list 1 2))
    """,
]

MANY_ARGS_COMPOSED_FORMS = [
    "((lambda () 1) 1 2 3 4 5)",
    "((lambda () false) true)",
    "((lambda ((x int) (y float) (z bool)) (list 1 2 3)) 1 2.3 true 2 4.5 false)",
    """
    (((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float)))
    (g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9))))
    (lambda ((a float)) 9e-1) (lambda () (lambda ((b int)) 9.9)))
    (lambda () (lambda ((a int)) 1.2)) (lambda ((a bool) (b int)) (list true)) (list 1 2 3))
    """,
    """
    (((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float)))
    (g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9))))
    (lambda ((a float)) 9e-1))
    (lambda () (lambda ((a int)) 1.2)) (lambda ((a bool) (b int)) (list true)) (list 1 2) (list 3))
    """,
]

INVALID_ARGS_COMPOSED_FORMS = [
    "((lambda ((a int)) true) false)",
    "((lambda ((b float)) 1) 2)",
    "((lambda ((c bool)) 1.0) 2.0)",
    "((lambda ((x int) (y float) (z bool)) (list 1 2 3)) 1 2.3 3)",
    "((lambda ((a float) (b int) (c bool)) true) 1.0 2.0 false)",
    "((lambda ((a int) (b bool) (c float)) true) 1.0 true 2.0)",
    "((lambda ((x int) (y float) (z bool)) (list 1 2 3)) 1.0 false 2)",
    "((lambda ((f (func (float bool) int))) 1) (lambda ((a float) (b int)) 1))",
    "((lambda ((f (func (float bool) int))) 1) (lambda ((a int) (b bool)) 1))",
    "((lambda ((f (func (float bool) int))) 1) (lambda ((a bool) (b float)) 1))",
    "((lambda ((f (func (float bool) int))) 1) (lambda ((a float) (b bool)) 1.0))",
    """
    (((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float)))
    (g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9))))
    (lambda ((a float)) 9e-1))
    (lambda () (lambda ((a int)) 1.2)) (lambda ((a bool) (b int)) (list true)) (list 1.1 2.2))
    """,
    """
    (((lambda ((g (func (float) float))) (lambda ((f (func () (func (int) float)))
    (g (func (bool int) (list bool))) (l (list int))) (list (lambda () 7.9))))
    (lambda ((a float) (b int)) 9e-1))
    (lambda () (lambda ((a int)) 1.2)) (lambda ((a bool) (b int)) (list true)) (list 1 2 3))
    """,
]


@pytest.mark.parametrize(["program", "type_"], VALID_LAMBDAS)
def test_lambda_typechecks(program: str, type_: FunctionType):
    program_node = parse(program)
    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize("program", INVALID_LAMBDA_BODIES)
def test_invalid_lambda_body_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("name", list(SpecialForm.forms_map.keys()) + ["nil"])
@pytest.mark.parametrize("program", INVALID_NAME_LAMBDAS)
def test_lambda_invalid_name_error(program: str, name: str, value: str):
    program_node = parse(program.format(name=name, return_val=value))

    with pytest.raises(exceptions.InvalidNameError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("program", DUPLICATE_NAME_LAMBDAS)
def test_lambda_duplicate_name_error(program: str, value: str):
    program_node = parse(program.format(return_val=value))

    with pytest.raises(exceptions.DuplicateNameError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("program", MISSING_ARGS_COMPOSED_FORMS)
def test_composed_form_missing_args_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("program", MANY_ARGS_COMPOSED_FORMS)
def test_composed_form_many_args_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("program", INVALID_ARGS_COMPOSED_FORMS)
def test_composed_form_invalid_args_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.TypeError):
        TypeChecker.check_program(program_node)
