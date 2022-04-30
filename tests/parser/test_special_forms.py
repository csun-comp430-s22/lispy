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


@pytest.mark.parametrize(["program", "elements"], VALID_LISTS)
def test_list_parses(program, elements):
    result = parse(program)

    assert result == Program((nodes.List(elements),))
