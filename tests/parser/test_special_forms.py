import pytest

from lispyc import nodes
from lispyc.exceptions import SpecialFormSyntaxError
from lispyc.nodes import ComposedForm, Constant, Program, Variable
from lispyc.parser import parse

VALID_VAR_ARGS = [
    ("($)", ()),
    ("($ 1 false 4.2 -7e1)", (Constant(1), Constant(False), Constant(4.2), Constant(-7e1))),
    ("($ (x false))", (ComposedForm(Variable("x"), (Constant(False),)),)),
    (
        "($ (list (list 1 2) (list 3 4)) (list a b))",
        (
            nodes.List(
                (nodes.List((Constant(1), Constant(2))), nodes.List((Constant(3), Constant(4))))
            ),
            nodes.List((Variable("a"), Variable("b"))),
        ),
    ),
]

VALID_2_ARGS = [
    ("($ a b)", Variable("a"), Variable("b")),
    (
        "($ (list a) (list b c))",
        nodes.List((Variable("a"),)),
        nodes.List((Variable("b"), Variable("c"))),
    ),
    ("($ (x 1) true)", ComposedForm(Variable("x"), (Constant(1),)), Constant(True)),
]

INVALID_2_ARGS = [
    "($)",
    "($ a)",
    "($ a b c)",
    "($ 1 2 a b c d true 17e-1)",
    "($ (x 1))",
    "($ (list b c))",
    "($ ($ 9 7))",
]

VALID_1_ARG = [
    ("($ a)", Variable("a")),
    ("($ 1)", Constant(1)),
    ("($ false)", Constant(False)),
    ("($ 1e-7)", Constant(1e-7)),
    ("($ (x 1))", ComposedForm(Variable("x"), (Constant(1),))),
    ("($ (list 1 2))", nodes.List((Constant(1), Constant(2)))),
]

INVALID_1_ARG = [
    "($)",
    "($ a b c)",
    "($ 1 2 a b c d true 17e-1)",
    "($ (x 1) 6)",
    "($ false (list b c))",
    "($ ($ y) (y 4))",
]

VALID_GE_2_ARGS = [
    VALID_VAR_ARGS[1],
    VALID_VAR_ARGS[3],
    *[(program, (arg1, arg2)) for program, arg1, arg2 in VALID_2_ARGS],
]

INVALID_GE_2_ARGS = [p for p, _ in VALID_1_ARG] + ["($)", "($ ($ x))", "($ ($ x y))"]


@pytest.mark.parametrize("node", [nodes.List])
@pytest.mark.parametrize(["program", "args"], VALID_VAR_ARGS)
def test_var_args_parses(program: str, args: tuple[nodes.Form, ...], node: type[nodes.SpecialForm]):
    result = parse(program.replace("$", node.id))

    assert result == Program((node(args),))


@pytest.mark.parametrize("node", [nodes.Cons])
@pytest.mark.parametrize(["program", "arg1", "arg2"], VALID_2_ARGS)
def test_2_args_parses(
    program: str, arg1: nodes.Form, arg2: nodes.Form, node: type[nodes.SpecialForm]
):
    result = parse(program.replace("$", node.id))

    assert result == Program((node(arg1, arg2),))


@pytest.mark.parametrize("node", [nodes.Cons])
@pytest.mark.parametrize("program", INVALID_2_ARGS)
def test_invalid_2_args_fails(program: str, node: type[nodes.SpecialForm]):
    with pytest.raises(SpecialFormSyntaxError):
        parse(program.replace("$", node.id))


@pytest.mark.parametrize("node", [nodes.Car, nodes.Cdr])
@pytest.mark.parametrize(["program", "arg"], VALID_1_ARG)
def test_1_arg_parses(program: str, arg: nodes.Form, node: type[nodes.SpecialForm]):
    result = parse(program.replace("$", node.id))

    assert result == Program((node(arg),))


@pytest.mark.parametrize("node", [nodes.Car, nodes.Cdr])
@pytest.mark.parametrize("program", INVALID_1_ARG)
def test_invalid_1_arg_fails(program: str, node: type[nodes.SpecialForm]):
    with pytest.raises(SpecialFormSyntaxError):
        parse(program.replace("$", node.id))


@pytest.mark.parametrize("node", [nodes.Progn])
@pytest.mark.parametrize(["program", "args"], VALID_GE_2_ARGS)
def test_ge_2_args_parses(
    program: str, args: tuple[nodes.Form, ...], node: type[nodes.SpecialForm]
):
    result = parse(program.replace("$", node.id))

    assert result == Program((node(args),))


@pytest.mark.parametrize("node", [nodes.Progn])
@pytest.mark.parametrize("program", INVALID_GE_2_ARGS)
def test_invalid_ge_2_args_fails(program: str, node: type[nodes.SpecialForm]):
    with pytest.raises(SpecialFormSyntaxError, match=f"{node.id}:"):
        parse(program.replace("$", node.id))
