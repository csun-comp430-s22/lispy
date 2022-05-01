import pytest

from lispyc.nodes import ComposedForm, Constant, Let, LetBinding, List, Program, Set, Variable
from lispyc.parser import parse

from .data import FORM_PROGRAMS, FORMS

SET_FORMS = FORMS + [("(set x 12)", Set(Variable("x"), Constant(12)))]
LET_FORMS = SET_FORMS + [
    (
        "((f 7) (g true))",
        ComposedForm(
            ComposedForm(Variable("f"), (Constant(7),)),
            (ComposedForm(Variable("g"), (Constant(True),)),),
        ),
    )
]
MULTIPLE_FORMS = ["1 2", "a b c", "false (x a b)", "(list 1) dx1", "() nil"]
INVALID_NAMES = ["()", "31", "false", "-1.2", "(list 3)", "(x (2 3))"]

MULTIPLE_LET = [
    (
        "(let ((x false) (Y_1 3)) $body$)",
        (LetBinding(Variable("x"), Constant(False)), LetBinding(Variable("Y_1"), Constant(3))),
    ),
    (
        "(let ((a x) (b (list 1 2)) (c (f 24)) (d (let ((z1 99)) 12)) (e (set j2j (x 1)))) $body$)",
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
    ),
    (
        "(let ((a1 21) (k1s nil)) $body$)",
        (LetBinding(Variable("a1"), Constant(21)), LetBinding(Variable("k1s"), Variable("nil"))),
    ),
]

MULTIPLE_BODY = [
    ("a 1 false", (Variable("a"), Constant(1), Constant(False))),
    ("(x a) nil ()", (ComposedForm(Variable("x"), (Variable("a"),)), Variable("nil"), List(()))),
    (
        f"5.6 1 {MULTIPLE_LET[0][0].replace('$body$', '()')} yZ true",
        (
            Constant(5.6),
            Constant(1),
            Let(MULTIPLE_LET[0][1], (List(()),)),
            Variable("yZ"),
            Constant(True),
        ),
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


@pytest.mark.parametrize(["program2", "form2"], LET_FORMS)
@pytest.mark.parametrize(["program1", "form1"], LET_FORMS)
def test_let_single_binding_and_form_parses(program1, program2, form1, form2):
    result = parse(f"(let ((aZ8__xe_2 {program1})) {program2})")

    assert result == Program((Let((LetBinding(Variable("aZ8__xe_2"), form1),), (form2,)),))


@pytest.mark.parametrize(["body_program", "body"], LET_FORMS)
@pytest.mark.parametrize(["program", "bindings"], MULTIPLE_LET)
def test_let_multiple_bindings_parses(program, body_program, bindings, body):
    program = program.replace("$body$", body_program)

    result = parse(program)

    assert result == Program((Let(bindings, (body,)),))


@pytest.mark.parametrize(["body_program", "body"], MULTIPLE_BODY)
@pytest.mark.parametrize(["program", "bindings"], MULTIPLE_LET)
def test_let_multiple_bindings_and_forms_parses(program, body_program, bindings, body):
    program = program.replace("$body$", body_program)

    result = parse(program)

    assert result == Program((Let(bindings, body),))
