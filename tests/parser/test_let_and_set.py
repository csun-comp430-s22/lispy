import pytest

from lispyc.nodes import Constant, Program, Set, Variable
from lispyc.parser import parse

from .data import FORM_PROGRAMS, FORMS

SET_FORMS = FORMS + [("(set x 12)", Set(Variable("x"), Constant(12)))]
MULTIPLE_FORMS = ["1 2", "a b c", "false (x a b)", "(list 1) dx1", "() nil"]
INVALID_NAMES = ["()", "31", "false", "-1.2", "(list 3)", "(x (2 3))"]


@pytest.mark.parametrize(["program", "form"], SET_FORMS)
def test_set_parses(program, form):
    name = "Zx___1D12e"
    result = parse(f"(set {name} {program})")

    assert result == Program((Set(Variable(name), form),))


def test_set_missing_form_fails():
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse("(set Zx___1D12e)")


@pytest.mark.parametrize("program", FORM_PROGRAMS)
def test_set_missing_name_fails(program):
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse(f"(set {program})")


@pytest.mark.parametrize("program", FORM_PROGRAMS)
@pytest.mark.parametrize("name", INVALID_NAMES)
def test_set_invalid_name_fails(name, program):
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse(f"(set {name} {program})")


@pytest.mark.parametrize("program", MULTIPLE_FORMS)
def test_set_multiple_forms_fails(program):
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse(f"(set Zx___1D12e {program})")


@pytest.mark.parametrize("program", MULTIPLE_FORMS)
def test_set_missing_name_multiple_forms_fails(program):
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse(f"(set {program})")
