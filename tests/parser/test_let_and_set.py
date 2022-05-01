import pytest

from lispyc.nodes import ComposedForm, Constant, Let, LetBinding, List, Program, Set, Variable
from lispyc.parser import parse

from .data import FORM_PROGRAMS, FORMS

SET_FORMS = FORMS + [("(set x 12)", Set(Variable("x"), Constant(12)))]
MULTIPLE_FORMS = ["1 2", "a b c", "false (x a b)", "(list 1) dx1", "() nil"]
INVALID_NAMES = ["()", "31", "false", "-1.2", "(list 3)", "(x (2 3))"]

MULTIPLE_LET = [
    (
        "(let ((x false) (Y_1 3)) ())",
        (LetBinding(Variable("x"), Constant(False)), LetBinding(Variable("Y_1"), Constant(3))),
        (List(()),),
    ),
    (
        "(let ((a x) (b (list 1 2)) (c (f 24)) (d (let ((z1 99)) 12)) (e (set j2j (x 1)))) body)",
        (
            LetBinding(Variable("a"), Variable("x")),
            LetBinding(Variable("b"), List((Constant(1), Constant(2)))),
            LetBinding(Variable("c"), ComposedForm(Variable("f"), (Constant(24),))),
            LetBinding(
                Variable("d"), Let((LetBinding(Variable("z1"), Constant(99)),), (Constant(12),))
            ),
            LetBinding(
                Variable("e"), Set(Variable("j2j"), ComposedForm(Variable("x"), (Constant(1),)))
            ),
        ),
        (Variable("body"),),
    ),
    (
        "(let ((a1 21) (k1s nil)) 2 (list 1) x)",
        (LetBinding(Variable("a1"), Constant(21)), LetBinding(Variable("k1s"), Variable("nil"))),
        (Constant(2), List((Constant(1),)), Variable("x")),
    ),
]


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


@pytest.mark.parametrize(["program2", "form2"], SET_FORMS)
@pytest.mark.parametrize(["program1", "form1"], SET_FORMS)
def test_let_single_binding_and_form_parses(program1, program2, form1, form2):
    result = parse(f"(let ((aZ8__xe_2 {program1})) {program2})")

    assert result == Program((Let((LetBinding(Variable("aZ8__xe_2"), form1),), (form2,)),))


@pytest.mark.parametrize(["program", "bindings", "body"], MULTIPLE_LET)
def test_let_multiple_bindings_and_forms_parses(program, bindings, body):
    result = parse(program)

    assert result == Program((Let(bindings, body),))
