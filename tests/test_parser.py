import math
import string

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

ATOMIC_LITERAL_PARAMS = ["a", "A", "dKa", "AxZ", "_", "_____", "_12", "c12", "d1G_", "atom2_3name1"]

INVALID_ATOM_PARAMS = [
    "0e",
    "12e",
    "9.e",
    "+",
    "-",
    "+e",
    "-e",
    ".",
    ".e123",
    "123atom",
    "+true",
    "-false",
    "my-atom",
    "-atomname",
    "äöåü",
    *[f"my{c}atom" for c in set(string.punctuation) - {"(", ")", "_"}],
]

LIST_PARAMS = [
    ("(+1)", [1]),
    ("(-2.4)", [-2.4]),
    ("(true)", [True]),
    ("(-inf)", [float("-inf")]),
    ("(false 12.3e2 -54 my_atom atom2 true)", [False, 12.3e2, -54, "my_atom", "atom2", True]),
    ("(9e-2 true +2.3 atom -92 atom1)", [9e-2, True, +2.3, "atom", -92, "atom1"]),
    ("()", []),
]


@pytest.mark.parametrize(["program", "value"], CONSTANT_PARAMS)
def test_constant(program, value):
    ast = parser.parse(program)

    assert ast == [value]


@pytest.mark.parametrize("program", ["nan", "+nan", "-nan"])
def test_nan(program):
    ast = parser.parse(program)

    assert len(ast.body) == 1
    atom = ast.body[0]
    assert isinstance(atom, nodes.Atom)
    assert math.isnan(atom.value)


@pytest.mark.parametrize("program", ATOMIC_LITERAL_PARAMS)
def test_atomic_literal(program):
    ast = parser.parse(program)

    assert ast == [program]


@pytest.mark.parametrize("program", INVALID_ATOM_PARAMS)
def test_invalid_atom(program):
    with pytest.raises(UnexpectedCharacters):
        parser.parse(program)


@pytest.mark.parametrize("program", ["1e", "()1e()", "(a b) 4dd", "77x (2 y)", "(5j)"])
def test_consecutive_atoms_require_whitespace(program):
    with pytest.raises(UnexpectedCharacters):
        parser.parse(program)


@pytest.mark.parametrize(["program", "value"], LIST_PARAMS)
def test_list(program, value):
    ast = parser.parse(program)

    assert ast == [value]
