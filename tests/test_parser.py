import math

import pytest
from lark.exceptions import UnexpectedCharacters

from lispyc import nodes, parser

CONSTANT_PARAMS = [
    ("true", True),
    ("false", False),
    ("123", 123),
    ("+123", +123),
    ("-123", -123),
    ("-23498734539485748724340897420334", -23498734539485748724340897420334),
    ("1.", 1.0),
    (".1", 0.1),
    ("1.0", 1.0),
    ("+1.0", +1.0),
    ("-1.0", -1.0),
    ("+2394.1298021", +2394.1298021),
    ("-0.0", -0.0),
    ("0e0", 0e0),
    ("000000000.0e000000000000", 000000000.0e000000000000),
    ("-0e+0", -0e0),
    ("1e3", 1e3),
    ("1.e3", 1.0e3),
    ("1.0e3", 1.0e3),
    ("+1.0e+3", +1.0e3),
    ("-1.0e-3", -1.0e-3),
    ("+123799.32489234e-3283293249", +123799.32489234e-3283293249),
    ("inf", float("inf")),
    ("+inf", float("+inf")),
    ("-inf", float("-inf")),
]


@pytest.mark.parametrize(["program", "value"], CONSTANT_PARAMS)
def test_constant(program, value):
    ast = parser.parse(program)

    assert len(ast.body) == 1
    atom = ast.body[0]
    assert isinstance(atom, nodes.Atom)
    assert atom.value == value


@pytest.mark.parametrize("program", ["nan", "+nan", "-nan"])
def test_nan(program):
    ast = parser.parse(program)

    assert len(ast.body) == 1
    atom = ast.body[0]
    assert isinstance(atom, nodes.Atom)
    assert math.isnan(atom.value)


@pytest.mark.parametrize("program", ["0e", "12e", "+", "-", "+e", "-e", ".", ".e123", "123atom"])
def test_invalid_atoms(program):
    with pytest.raises(UnexpectedCharacters):
        parser.parse(program)
