import pytest

from lispyc import nodes
from lispyc.nodes import ComposedForm, Constant, Program, Variable
from lispyc.parser import parse

CONSTANT_PARAMS = [
    ("1", 1),
    ("-44", -44),
    ("1.35", 1.35),
    ("-2e-7", -2e-7),
    ("false", False),
    ("true", True),
]

COMPOSED_FORM_PARAMS = [
    ("(myfunc 1 2)", Variable("myfunc"), (Constant(1), Constant(2))),
    ("(1 false)", Constant(1), (Constant(False),)),
    ("(true)", Constant(True), ()),
    ("(0e0 C3_7e)", Constant(0e0), (Variable("C3_7e"),)),
    (
        "((retfunc a_1 -2e7) arg1 (x y Z))",
        ComposedForm(Variable("retfunc"), (Variable("a_1"), Constant(-2e7))),
        (
            Variable("arg1"),
            ComposedForm(Variable("x"), (Variable("y"), Variable("Z"))),
        ),
    ),
    (
        "((a (b 2) 1) (c (d (e 5) 4) 3) 70 80 90)",
        ComposedForm(Variable("a"), (ComposedForm(Variable("b"), (Constant(2),)), Constant(1))),
        (
            ComposedForm(
                Variable("c"),
                (
                    ComposedForm(
                        Variable("d"), (ComposedForm(Variable("e"), (Constant(5),)), Constant(4))
                    ),
                    Constant(3),
                ),
            ),
            Constant(70),
            Constant(80),
            Constant(90),
        ),
    ),
]


@pytest.mark.parametrize("program", ["x", "y1", "z_A", "C", "nil", "not", "float"])
def test_variable_parses(program):
    result = parse(program)

    assert result == Program((Variable(program),))


@pytest.mark.parametrize(["program", "value"], CONSTANT_PARAMS)
def test_constant_parses(program, value):
    result = parse(program)

    assert result == Program((Constant(value),))


def test_empty_list_parses():
    result = parse("()")

    assert result == Program((nodes.List(()),))


@pytest.mark.parametrize(["program", "name", "args"], COMPOSED_FORM_PARAMS)
def test_composed_form_parses(program, name, args):
    result = parse(program)

    assert result == Program((ComposedForm(name, args),))
