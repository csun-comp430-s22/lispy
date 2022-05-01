import pytest

from lispyc import nodes
from lispyc.nodes import ComposedForm, Constant, List, Program, Variable
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

MULTIPLE_PROGRAMS = [
    (
        "a 2 false () 7.9 nil",
        (Variable("a"), Constant(2), Constant(False), List(()), Constant(7.9), Variable("nil")),
    ),
    (
        f"(myfunc 1 2) true (list 4 5) {COMPOSED_FORM_PARAMS[5][0]} 9e-3",
        (
            (ComposedForm(Variable("myfunc"), (Constant(1), Constant(2)))),
            Constant(True),
            List((Constant(4), Constant(5))),
            ComposedForm(COMPOSED_FORM_PARAMS[5][1], COMPOSED_FORM_PARAMS[5][2]),
            Constant(9e-3),
        ),
    ),
    (
        "(define f ((x int) (y float)) (list x y)) (f 1 2.5)",
        (
            nodes.Define(
                Variable("f"),
                (
                    nodes.FunctionParameter(Variable("x"), nodes.IntType()),
                    nodes.FunctionParameter(Variable("y"), nodes.FloatType()),
                ),
                List((Variable("x"), Variable("y"))),
            ),
            ComposedForm(Variable("f"), (Constant(1), Constant(2.5))),
        ),
    ),
]

INVALID_MULTIPLE_PROGRAMS = [
    "a b (define) 12 ()",
    "false 82 (car 1 2 3)",
    "(x 3) 7.8 (cons 19) (list 2) 1 (select a b c)",
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

    assert result == Program((List(()),))


@pytest.mark.parametrize(["program", "name", "args"], COMPOSED_FORM_PARAMS)
def test_composed_form_parses(program, name, args):
    result = parse(program)

    assert result == Program((ComposedForm(name, args),))


@pytest.mark.parametrize(["program", "nodes_"], MULTIPLE_PROGRAMS)
def test_multiple_programs_parses(program, nodes_):
    result = parse(program)

    assert result == Program(nodes_)


@pytest.mark.parametrize("program", INVALID_MULTIPLE_PROGRAMS)
def test_multiple_programs_propagates_failures(program):
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse(program)
