import pytest

from lispyc import nodes
from lispyc.nodes import ComposedForm, Constant, Program, Variable
from lispyc.parser import parse

VALID_LISTS = [
    ("(list)", ()),
    ("(list 1 false 4.2 -7e1)", (Constant(1), Constant(False), Constant(4.2), Constant(-7e1))),
    ("(list (x false))", (ComposedForm(Variable("x"), (Constant(False),)),)),
    (
        "(list (list (list 1 2) (list 3 4)) (list a b))",
        (
            nodes.List(
                (nodes.List((Constant(1), Constant(2))), nodes.List((Constant(3), Constant(4))))
            ),
            nodes.List((Variable("a"), Variable("b"))),
        ),
    ),
]


VALID_CONS = [
    ("(cons a b)", Variable("a"), Variable("b")),
    (
        "(cons (list a) (list b c))",
        nodes.List((Variable("a"),)),
        nodes.List((Variable("b"), Variable("c"))),
    ),
    ("(cons (x 1) true)", ComposedForm(Variable("x"), (Constant(1),)), Constant(True)),
]

INVALID_CONS = [
    "(cons)",
    "(cons a)",
    "(cons a b c)",
    "(cons 1 2 a b c d true 17e-1)",
]


@pytest.mark.parametrize(["program", "elements"], VALID_LISTS)
def test_list_parses(program, elements):
    result = parse(program)

    assert result == Program((nodes.List(elements),))


@pytest.mark.parametrize(["program", "car", "cdr"], VALID_CONS)
def test_cons_parses(program, car, cdr):
    result = parse(program)

    assert result == Program((nodes.Cons(car, cdr),))


@pytest.mark.parametrize("program", INVALID_CONS)
def test_invalid_cons_fails(program):
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse(program)
