import pytest

from lispyc import exceptions
from lispyc.nodes import FloatType, ListType, SpecialForm
from lispyc.parser import parse
from lispyc.typechecker import TypeChecker

VALUES = ["1", "1e-2", "false", "(list 1 2 3)", "(lambda ((j int) (k float)) 13)"]

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


def test_let_set_typechecks():
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
