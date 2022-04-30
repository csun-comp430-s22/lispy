import pytest

from lispyc import nodes
from lispyc.nodes import ComposedForm, Constant
from lispyc.nodes import FunctionParameter as Param
from lispyc.nodes import Program, Variable, types
from lispyc.parser import parse

LAMBDA_PARAMS = [
    ("(lambda () ())", (), nodes.List(())),
    (
        "(lambda ((int int) (bool bool) (float float)) (Y b 123))",
        (
            Param(Variable("int"), types.IntType()),
            Param(Variable("bool"), types.BoolType()),
            Param(Variable("float"), types.FloatType()),
        ),
        ComposedForm(Variable("Y"), (Variable("b"), Constant(123))),
    ),
    (
        "(lambda ((a int)) (1.2 (a -44) false))",
        (Param(Variable("a"), types.IntType()),),
        ComposedForm(
            Constant(1.2), (ComposedForm(Variable("a"), (Constant(-44),)), Constant(False))
        ),
    ),
    (
        "(lambda ((func (func ((list int) float) bool)) (list (list float))) (j__9e (true d)))",
        (
            Param(
                Variable("func"),
                types.FunctionType(
                    (types.ListType(types.IntType()), types.FloatType()), types.BoolType()
                ),
            ),
            Param(Variable("list"), types.ListType(types.FloatType())),
        ),
        ComposedForm(Variable("j__9e"), (ComposedForm(Constant(True), (Variable("d"),)),)),
    ),
    (
        "(lambda ((f (func () (func (int) float)))) 1)",
        (
            Param(
                Variable("f"),
                types.FunctionType((), types.FunctionType((types.IntType(),), types.FloatType())),
            ),
        ),
        Constant(1),
    ),
]

INVALID_LAMBDA_PARAMS = [
    "(lambda)",  # Missing params and body.
    "(lambda ())",  # Missing params or body.
    "(lambda ((x int) (y str)))",  # Missing body.
    "(lambda (x 1 2))",  # Missing params.
    "(lambda (x int) ())",  # Param not nested.
    "(lambda (()) ())",  # Empty param.
]


@pytest.mark.parametrize(["program", "params", "body"], LAMBDA_PARAMS)
def test_lambda_parses(program, params, body):
    result = parse(program)

    assert result == Program((nodes.Lambda(params, body),))


@pytest.mark.parametrize("program", INVALID_LAMBDA_PARAMS)
def test_invalid_lambda_fails(program):
    with pytest.raises(ValueError):  # noqa: PT011  # TODO: Use custom exception type.
        parse(program)
