import pytest

from lispyc import nodes
from lispyc.exceptions import SpecialFormSyntaxError
from lispyc.nodes import Branch, ComposedForm, Cond, Constant, Program, Variable
from lispyc.parser import parse

from .data import FORM_PROGRAMS, FORMS

VALID_1_BRANCH_PROGRAMS = [
    "($name$ $value$ ((x 7 y) (a b)) $default$)",
    "($name$ $value$ ((cond (a b) 1.7) ()) $default$)",
]

VALID_PROGRAMS = [
    "($name$ $value$ (a 7.9) (1 true) $default$)",
    "($name$ $value$ ((x 7 y) (a b)) ((cond (a b) false) ()) $default$)",
]

VALID_NODES = [
    (Branch(Variable("a"), Constant(7.9)), Branch(Constant(1), Constant(True))),
    (
        Branch(
            ComposedForm(Variable("x"), (Constant(7), Variable("y"))),
            ComposedForm(Variable("a"), (Variable("b"),)),
        ),
        Branch(Cond((Branch(Variable("a"), Variable("b")),), Constant(False)), nodes.List(())),
    ),
]

VALID = list(zip(VALID_PROGRAMS, VALID_NODES))


def replace(program: str, name: str, value: str, default: str) -> str:
    return program.replace("$name$", name).replace("$value$", value).replace("$default$", default)


@pytest.mark.parametrize(["default_program", "default"], FORMS)
@pytest.mark.parametrize(["program", "branches"], VALID)
def test_cond_parses(
    program: str, default_program: str, branches: tuple[Branch, ...], default: nodes.Form
):
    program = replace(program, "cond", "", default_program)

    result = parse(program)

    assert result == Program((nodes.Cond(branches, default),))


@pytest.mark.parametrize(["default_program", "default"], FORMS)
@pytest.mark.parametrize(["value_program", "value"], FORMS)
@pytest.mark.parametrize(["program", "branches"], VALID)
def test_select_parses(
    program: str,
    value_program: str,
    default_program: str,
    value: nodes.Form,
    branches: tuple[Branch, ...],
    default: nodes.Form,
):
    program = replace(program, "select", value_program, default_program)

    result = parse(program)

    assert result == Program((nodes.Select(value, branches, default),))


@pytest.mark.parametrize("default", FORM_PROGRAMS)
def test_cond_missing_branches_fails(default: str):
    with pytest.raises(SpecialFormSyntaxError, match="cond:"):
        parse(f"(cond {default})")


@pytest.mark.parametrize("value", FORM_PROGRAMS)
@pytest.mark.parametrize("program", VALID_PROGRAMS)
def test_cond_with_value_fails(program: str, value: str):
    program = replace(program, "cond", value, "false")

    with pytest.raises(SpecialFormSyntaxError, match="branch:"):
        parse(program)


@pytest.mark.parametrize("program", VALID_1_BRANCH_PROGRAMS)
def test_cond_missing_default_fails(program: str):
    program = replace(program, "cond", "", "")

    with pytest.raises(SpecialFormSyntaxError, match="cond:"):
        parse(program)


@pytest.mark.parametrize("invalid_branch", FORM_PROGRAMS)
@pytest.mark.parametrize("program", VALID_PROGRAMS)
def test_cond_invalid_branch_fails(program: str, invalid_branch: str):
    program = replace(program, "cond", "", f"{invalid_branch} 12")

    with pytest.raises(SpecialFormSyntaxError, match="branch:"):
        parse(program)


@pytest.mark.parametrize("default", FORM_PROGRAMS)
@pytest.mark.parametrize("value", FORM_PROGRAMS)
def test_select_missing_branches_fails(value: str, default: str):
    with pytest.raises(SpecialFormSyntaxError, match="select:"):
        parse(f"(select {value} {default})")


@pytest.mark.parametrize("program", VALID_1_BRANCH_PROGRAMS)
def test_select_missing_value_and_default_fails(program: str):
    program = replace(program, "select", "", "")

    with pytest.raises(SpecialFormSyntaxError, match="select:"):
        parse(program)


@pytest.mark.parametrize("value", FORM_PROGRAMS)
@pytest.mark.parametrize("program", VALID_1_BRANCH_PROGRAMS)
def test_select_missing_default_fails(program: str, value: str):
    program = replace(program, "select", value, "")

    with pytest.raises(SpecialFormSyntaxError, match="select:"):
        parse(program)


@pytest.mark.parametrize("invalid_branch", FORM_PROGRAMS)
@pytest.mark.parametrize("program", VALID_PROGRAMS)
def test_select_invalid_branch_fails(program: str, invalid_branch: str):
    program = replace(program, "select", "a", f"{invalid_branch} 12")

    with pytest.raises(SpecialFormSyntaxError, match="branch:"):
        parse(program)
