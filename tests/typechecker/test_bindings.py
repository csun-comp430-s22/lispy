import pytest

from lispyc import exceptions
from lispyc.nodes import BoolType, FloatType, FunctionType, IntType, ListType, SpecialForm, Type
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

VALUES = ["1", "1e-2", "false", "(list 1 2 3)", "(lambda ((j int) (k float)) 13)"]

VALID_SETS = [
    ("(let ((a 1)) (set a 2))", IntType()),
    ("(let ((a 1.0)) (set a 2.0))", FloatType()),
    ("(let ((a false)) (set a true))", BoolType()),
    ("(let ((a (list 1))) (set a (list 1 2 3)))", ListType(IntType())),
    (
        "(let ((a (lambda ((x int) (y float)) 1))) (set a (lambda ((j int) (k float)) 13)))",
        FunctionType((IntType(), FloatType()), IntType()),
    ),
    ("(let ((a 1.0)) (set a (set a 2.0)))", FloatType()),
    ("(let ((a 1) (b 5)) (set b (set a 3)))", IntType()),
    ("(let ((a nil)) (set a (list 1 2)) a)", ListType(IntType())),
    ("(lambda ((x int)) (set x 2))", FunctionType((IntType(),), IntType())),
    ("(lambda ((x float)) (set x 2.0))", FunctionType((FloatType(),), FloatType())),
    ("(lambda ((x bool)) (set x false))", FunctionType((BoolType(),), BoolType())),
    (
        "(lambda ((x (list int))) (set x (list 1)))",
        FunctionType((ListType(IntType()),), ListType(IntType())),
    ),
    (
        "(lambda ((x (func (int) float))) (set x (lambda ((j int)) 2.0)))",
        FunctionType(
            (FunctionType((IntType(),), FloatType()),), FunctionType((IntType(),), FloatType())
        ),
    ),
]

SCOPE_TEST_LAMBDAS = [
    (
        "(lambda ((a int) (b float)) (progn a b))",
        FunctionType((IntType(), FloatType()), FloatType()),
    ),
    (
        "(lambda ((a int) (b float)) (progn a b (let ((c 1) (d false)) a b c d) a b))",
        FunctionType((IntType(), FloatType()), FloatType()),
    ),
]

SCOPE_TEST_LETS = [
    ("(let ((a 1) (b 2.0)) a b)", FloatType()),
    ("(let ((a 1) (b 2.0)) a b (let ((b 3.0)) a b) a b)", FloatType()),
    ("(let ((a 1) (b 2.0)) a b (lambda ((c bool)) (progn a b c)) a b)", FloatType()),
    (
        "(let ((a 1) (b 2.0) (c false) (d (list 1 2))) "
        "a b c d (let ((e 2) (f false)) a b c d e f) d b c a)",
        IntType(),
    ),
]

SCOPE_TEST_SETS = [
    ("(let ((a 1) (b 2.0) (c false) (d (list 1 2))) (set c true) d b c a)", IntType()),
    ("(let ((a 1) (b false)) (let ((b 2.0)) a b) (set a 2) a b)", BoolType()),
    ("(let ((a 1) (b false)) (let ((b 2.0)) (set a 2)) a b)", BoolType()),
    ("(let ((a 1) (b false)) (let ((b 2.0)) (set a 2) a b) (set a 2) a b)", BoolType()),
    (
        "(lambda ((a int) (b bool)) (progn a b (set a 1) a b))",
        FunctionType((IntType(), BoolType()), BoolType()),
    ),
    (
        "(lambda ((a int) (b bool)) (lambda ((c float)) (progn a b c (set a 1) a b c)))",
        FunctionType((IntType(), BoolType()), FunctionType((FloatType(),), FloatType())),
    ),
]

SHADOWING = [
    (
        "(lambda ((a int) (b float)) (lambda ((a bool)) a))",
        FunctionType((IntType(), FloatType()), FunctionType((BoolType(),), BoolType())),
    ),
    (
        "(lambda ((a int) (b float)) (progn (lambda ((a bool)) a) b a))",
        FunctionType((IntType(), FloatType()), IntType()),
    ),
    (
        "(lambda ((a int) (b float)) (let ((a false)) a))",
        FunctionType((IntType(), FloatType()), BoolType()),
    ),
    (
        "(lambda ((a int) (b float)) (progn (let ((a false)) a) b a))",
        FunctionType((IntType(), FloatType()), IntType()),
    ),
    ("(let ((a 1) (b 2.0)) (let ((a true)) a))", BoolType()),
    ("(let ((a 1) (b 2.0)) (let ((a true)) a) a)", IntType()),
    ("(let ((a 1) (b 2.0)) (lambda ((a bool)) a))", FunctionType((BoolType(),), BoolType())),
    ("(let ((a 1) (b 2.0)) (lambda ((a bool)) a) a)", IntType()),
]

INVALID_NAME_LETS = [
    "(let (({name} 1.0)) {return_val})",
    "(let (({name} (list 1))) {return_val})",
    "(let (({name} (lambda ((a int)) 1.0))) {return_val})",
    "(let (({name} 1) ({name} 2.0)) {return_val})",
    "(let ((y 1) ({name} false) (x 1.0)) {return_val})",
    "(let (({name} false)) (let (({name} 1.0)) {return_val}))",
]

DUPLICATE_NAME_LETS = [
    "(let ((x 1) (x 2)) {return_val})",
    "(let ((x true) (y 1) (x false)) {return_val})",
    "(let ((z_Y 1) (z_Y 2.0)) {return_val})",
    "(let ((j 1) (j 2.0)) {return_val})",
    "(let ((a2 1)) (let ((b 1.0) (b 2)) {return_val}))",
]

INVALID_NAME_SETS = [
    "(set {name} {value})",
    "(let ((a {value})) (set a (set {name} {value})))",
    "(let ((a 1)) (set {name} {value}))",
    "(let ((a 1)) (let ((b 2)) (set {name} {value})))",
    "(lambda ((a int)) (set {name} {value}))",
]

UNBOUND_NAME_SETS = [
    "(set x 1)",
    "(set x (set y 1))",
    "(lambda ((a int)) (set b 1))",
    "(lambda ((a float)) a) (set a 2.1)",
    "((lambda ((a float)) a) (set a 2.1))",
    "(lambda ((a float)) (progn (lambda ((b int)) b) (set b 1)))",
    "(lambda ((a float)) (progn (set b 1) (lambda ((b int)) b)))",
    "(let ((a 1) (b 2)) (set c 3))",
    "(let ((x false)) x) (set x true)",
    "(let ((a (let ((b 1)) b))) (set b 2))",
]

INVALID_VALUE_SETS = [
    "(let ((a 1) (b 2)) (set a 3.0))",
    "(let ((a false) (b 1) (c 1.0)) (set b true))",
    "(let ((a 1)) (let ((a false)) (set a 2)))",
    "(let ((a 1)) (let ((a false)) a) (set a true))",
    "(lambda ((a float)) (set a 1))",
    "(lambda ((a int)) (lambda ((a bool)) (set a 2)))",
    "(lambda ((a int)) (progn (set a false) (lambda ((a bool)) a)))",
    "(lambda ((a int)) (progn (lambda ((a bool)) a) (set a false)))",
]

UNBOUND_NAME_REFERENCES = [
    "a",
    "(list x)",
    "(list 1 x 2)",
    "(progn x y z)",
    "(lambda ((a int)) b)",
    "(lambda ((a int)) a) b",
    "(let ((a 1)) b)",
    "(let ((a 1)) b (let ((b 2)) b))",
    "(let ((a 1)) (let ((b 2)) b) b)",
    "(let ((a (let ((b 2)) b))) b)",
]

SPECIAL_FORM_NAME_REFERENCES = [
    "{name}",
    "(list {name})",
    "(let ((a {name})) a)",
    "(let ((a (lambda () nil))) (set a {name}))",
    "(lambda ((f (func () int))) (set f {name}))",
    "((lambda ((f (func () int))) (f)) {name})",
]

PREMATURE_REFERENCE_LETS = [
    "(let ((a 1) (b a)) nil)",
    "(let ((a b) (b false)) nil)",
    "(let ((a 1) (b (let ((c a)) nil))) nil)",
]


@pytest.mark.parametrize(["program", "type_"], VALID_SETS)
def test_set_typechecks(program: str, type_: Type):
    program_node = parse(program)

    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize(["program", "type_"], SCOPE_TEST_LAMBDAS)
def test_lambda_names_in_scope(program: str, type_: Type):
    program_node = parse(program)

    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize(["program", "type_"], SCOPE_TEST_LETS)
def test_let_names_in_scope(program: str, type_: Type):
    program_node = parse(program)

    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize(["program", "type_"], SCOPE_TEST_SETS)
def test_set_other_names_remain_in_scope(program: str, type_: Type):
    program_node = parse(program)

    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


@pytest.mark.parametrize(["program", "type_"], SHADOWING)
def test_set_shadowing(program: str, type_: Type):
    program_node = parse(program)

    result = list(TypeChecker.check_program(program_node))

    assert result == [type_]


def test_complex_let_set_typechecks():
    program = """
    (let
        (
            (a (lambda ((a int) (b int)) (let ((c 3)) (list a b c))))
            (b (lambda ((c float) (d float)) (progn (set c 5.0) (list c d))))
            (d 6.5)
            (e nil)
        )
        (set d -1.0)
        (a 1 2)
        (set e (list 1e1 2e2))
        (cdr (b (car e) 3e3))
    )
    """
    program_node = parse(program)

    result = list(TypeChecker.check_program(program_node))

    assert result == [ListType(FloatType())]


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("name", list(SpecialForm.forms_map.keys()) + ["nil"])
@pytest.mark.parametrize("program", INVALID_NAME_LETS)
def test_let_invalid_name_error(program: str, name: str, value: str):
    program_node = parse(program.format(name=name, return_val=value))

    with pytest.raises(exceptions.InvalidNameError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("program", DUPLICATE_NAME_LETS)
def test_let_duplicate_name_error(program: str, value: str):
    program_node = parse(program.format(return_val=value))

    with pytest.raises(exceptions.DuplicateNameError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("name", list(SpecialForm.forms_map.keys()) + ["nil"])
@pytest.mark.parametrize("program", INVALID_NAME_SETS)
def test_set_invalid_name_error(program: str, name: str, value: str):
    program_node = parse(program.format(name=name, value=value))

    with pytest.raises(exceptions.InvalidNameError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("program", UNBOUND_NAME_SETS)
def test_set_unbound_name_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.UnboundNameError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("program", INVALID_VALUE_SETS)
def test_set_invalid_value_type_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.UnificationError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("program", UNBOUND_NAME_REFERENCES)
def test_reference_unbound_name_error(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.UnboundNameError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("name", SpecialForm.forms_map.keys())
@pytest.mark.parametrize("program", SPECIAL_FORM_NAME_REFERENCES)
def test_special_form_reference_syntax_error(program: str, name: str):
    program_node = parse(program.format(name=name))

    with pytest.raises(exceptions.SpecialFormSyntaxError):
        TypeChecker.check_program(program_node)


@pytest.mark.parametrize("program", PREMATURE_REFERENCE_LETS)
def test_let_binds_in_parallel(program: str):
    program_node = parse(program)

    with pytest.raises(exceptions.UnboundNameError):
        TypeChecker.check_program(program_node)
