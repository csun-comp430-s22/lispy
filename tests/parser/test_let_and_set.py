import pytest

from lispyc.exceptions import SpecialFormSyntaxError
from lispyc.nodes import ComposedForm, Constant, Let, LetBinding, List, Program, Set, Variable
from lispyc.parser import parse

from .data import FORM_PROGRAMS, FORMS, MULTIPLE_FORM_PROGRAMS, MULTIPLE_FORMS

INVALID_NAMES = ["()", "31", "false", "-1.2", "(list 3)", "(x (2 3))"]

SET_FORM = ("(set x 12)", Set(Variable("x"), Constant(12)))
LET_BINDING = (
    "((f 7) (g true))",
    ComposedForm(
        ComposedForm(Variable("f"), (Constant(7),)),
        (ComposedForm(Variable("g"), (Constant(True),)),),
    ),
)

FORMS_WITH_SET = FORMS + [SET_FORM]
FORMS_WITH_SET_AND_BINDING = FORMS_WITH_SET + [LET_BINDING]

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

MULTIPLE_FORMS_WITH_LET = MULTIPLE_FORMS + [
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

LET_WITH_INVALID_BINDINGS = [
    "(let (()) ())",
    "(let (a b c) 23)",
    "(let ((x y) (z)) (body stuff))",
    "(let ((name value) (2 f) (name2 (f 1))) (1 2 3.5))",
    "(let ((n (list 2 3)) (x u) 4.5 (d e)) body)",
]


@pytest.mark.parametrize(["program", "form"], FORMS_WITH_SET)
def test_set_parses(program, form):
    name = "Zx___1D12e"
    result = parse(f"(set {name} {program})")

    assert result == Program((Set(Variable(name), form),))


def test_set_missing_form_fails():
    with pytest.raises(SpecialFormSyntaxError, match="set:"):
        parse("(set Zx___1D12e)")


@pytest.mark.parametrize("program", FORM_PROGRAMS)
def test_set_missing_name_fails(program):
    with pytest.raises(SpecialFormSyntaxError, match="set:"):
        parse(f"(set {program})")


@pytest.mark.parametrize("program", FORM_PROGRAMS)
@pytest.mark.parametrize("name", INVALID_NAMES)
def test_set_invalid_name_fails(name, program):
    with pytest.raises(SpecialFormSyntaxError, match="set:"):
        parse(f"(set {name} {program})")


@pytest.mark.parametrize("program", MULTIPLE_FORM_PROGRAMS)
def test_set_multiple_forms_fails(program):
    with pytest.raises(SpecialFormSyntaxError, match="set:"):
        parse(f"(set Zx___1D12e {program})")


@pytest.mark.parametrize("program", MULTIPLE_FORM_PROGRAMS)
def test_set_missing_name_multiple_forms_fails(program):
    with pytest.raises(SpecialFormSyntaxError, match="set:"):
        parse(f"(set {program})")


@pytest.mark.parametrize(["body_program", "body"], FORMS_WITH_SET_AND_BINDING)
@pytest.mark.parametrize(["binding_program", "binding"], FORMS_WITH_SET_AND_BINDING)
def test_let_single_binding_and_body_parses(binding_program, body_program, binding, body):
    result = parse(f"(let ((aZ8__xe_2 {binding_program})) {body_program})")

    assert result == Program((Let((LetBinding(Variable("aZ8__xe_2"), binding),), (body,)),))


@pytest.mark.parametrize(["body_program", "body"], FORMS_WITH_SET_AND_BINDING)
@pytest.mark.parametrize(["program", "bindings"], MULTIPLE_LET)
def test_let_multiple_bindings_parses(program, body_program, bindings, body):
    program = program.replace("$body$", body_program)

    result = parse(program)

    assert result == Program((Let(bindings, (body,)),))


@pytest.mark.parametrize(["body_program", "body"], MULTIPLE_FORMS_WITH_LET)
@pytest.mark.parametrize(["program", "bindings"], MULTIPLE_LET)
def test_let_multiple_bindings_and_body_parses(program, body_program, bindings, body):
    program = program.replace("$body$", body_program)

    result = parse(program)

    assert result == Program((Let(bindings, body),))


@pytest.mark.parametrize(["program", "form"], FORMS_WITH_SET_AND_BINDING)
def test_let_single_binding_missing_body_fails(program, form):
    with pytest.raises(SpecialFormSyntaxError, match="let:"):
        parse(f"(let ((aZ8__xe_2 {program})))")


@pytest.mark.parametrize(["program", "bindings"], MULTIPLE_LET)
def test_let_multiple_bindings_missing_body_fails(program, bindings):
    program = program.replace("$body$", "")

    with pytest.raises(SpecialFormSyntaxError, match="let:"):
        parse(program)


@pytest.mark.parametrize(["program", "body"], FORMS_WITH_SET)
def test_let_missing_bindings_single_body_fails(program, body):
    with pytest.raises(SpecialFormSyntaxError, match="let:"):
        parse(f"(let {program})")


@pytest.mark.parametrize(["program", "body"], MULTIPLE_FORMS_WITH_LET)
def test_let_missing_bindings_multiple_body_fails(program, body):
    with pytest.raises(SpecialFormSyntaxError, match=r"let( binding)?:"):
        parse(f"(let {program})")


@pytest.mark.parametrize("program", LET_WITH_INVALID_BINDINGS)
def test_let_invalid_bindings_fails(program):
    with pytest.raises(SpecialFormSyntaxError, match="let binding:"):
        parse(program)
