import pytest

from lispyc import nodes
from lispyc.parser import parse

CONSTANTS = [
    ("1", 1),
    ("-44", -44),
    ("1.35", 1.35),
    ("-2e-7", -2e-7),
    ("false", False),
    ("true", True),
]


@pytest.mark.parametrize("program", ["x", "y1", "z_A", "C"])
def test_variable_parses(program):
    result = parse(program)

    assert result == nodes.Program((nodes.Variable(program),))


@pytest.mark.parametrize(["program", "value"], CONSTANTS)
def test_constant_parses(program, value):
    result = parse(program)

    assert result == nodes.Program((nodes.Constant(value),))


def test_empty_list_parses():
    result = parse("()")

    assert result == nodes.Program((nodes.List(()),))
