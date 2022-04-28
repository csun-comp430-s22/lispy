import math
import random
import string

import pytest
from lark.exceptions import UnexpectedCharacters, UnexpectedInput

from sexpression import nodes, parser

random.seed(1)

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
    *[f"my{c}atom" for c in string.punctuation if c not in {"(", ")", "_", "$"}],
]

LIST_PARAMS = [
    ("$($+1$)$", [1]),
    ("$($-2.4$)$", [-2.4]),
    ("$($true$)$", [True]),
    ("$($-inf$)$", [float("-inf")]),
    (
        "$($false$ $12.3e2$ $-54$ $my_atom$ $atom2$ $true$)$",
        [False, 12.3e2, -54, "my_atom", "atom2", True],
    ),
    ("$($9e-2$ $true$ $+2.3$ $atom$ $-92$ $atom1$)$", [9e-2, True, +2.3, "atom", -92, "atom1"]),
    ("$($)$", []),
]

LIST_NESTED_PARAMS = [
    ("$($a$($b $c$)$)$", [["a", ["b", "c"]]]),
    ("$($($a $b$)$($1$)$2$)$($($)$)$", [[["a", "b"], [1], 2], [[]]]),
    (
        "$($($($bb$($($a$)$($x$)$c$($($)$)$$true$)$1)$f$)$1e12 $c$)"
        "$($($9$($($1.2$)$($)$)$($d$)$($)$)$)$",
        [
            [[["bb", [["a"], ["x"], "c", [[]], True], 1], "f"], 1e12, "c"],
            [[9, [[1.2], []], ["d"], []]],
        ],
    ),
]

PROGRAM_SIMPLE_PARAMS = [
    ("$($)$1$($)$", [[], 1, []]),
    ("$1$($)$1$", [1, [], 1]),
    ("$1$($)$", [1, []]),
    ("$($)$1$", [[], 1]),
    ("$1$($)$($)$", [1, [], []]),
    ("$($)$($)$1$", [[], [], 1]),
    ("$1$ $1$($)$", [1, 1, []]),
    ("$($)$1$ $1$", [[], 1, 1]),
]

PROGRAM_PARAMS = [
    (
        "$($atom$ $-23$ $true$)$ $($2e-7$ $x$ $false$)$ $($)$ $($)$ $($x$)$",
        [["atom", -23, True], [2e-7, "x", False], [], [], ["x"]],
    ),
    (
        "$($+inf$ $11$)$ $9$ $true$ $($x1$ $y$ $.12$)$ $z23$ $($)$",
        [[float("+inf"), 11], 9, True, ["x1", "y", 0.12], "z23", []],
    ),
    (
        "$($list$ $1$ $2$)$($true$ $false$ $1$)$x$ $1$($y$ $a2b$)$($)$($)$1$ $a$",
        [["list", 1, 2], [True, False, 1], "x", 1, ["y", "a2b"], [], [], 1, "a"],
    ),
    ("$z2a$ $2$($atom$ $7$ $a$)$", ["z2a", 2, ["atom", 7, "a"]]),
    ("$($a$ $1$ $true$)$false$($-2e+1$ $3$)$", [["a", 1, True], False, [-2e1, 3]]),
    ("$inf$($x$ $-1$)$false$", [float("inf"), ["x", -1], False]),
]

MISSING_PAREN_PARAMS = [
    "$($",
    "$)$",
    "$)$)$",
    "$($($",
    "$($)$($",
    "$($)$)$",
    "$($($)$",
    "$)$($)$",
    "$($($($($)$)$)$)$)$",
    "$($($($($($($)$)$)$)$)$",
    "$($)$($)$($($)$($)$",
    "$($)$($)$)$($)$($)$",
    "$($($)$)$($)$($",
    "$($a$ $1$($c$($d$)$)$)$($e$)$)$",
    "$a$)",
    "$($a",
]


def inject_random_ws(program: str, placeholder: str) -> str:
    ws = " \t\f\r\n"

    output = ""
    for c in program:
        if c == placeholder:
            c = "".join(random.choices(ws, k=random.randint(2, 100)))

        output += c

    return output


@pytest.mark.parametrize(["program", "value"], CONSTANT_PARAMS)
def test_constant(program, value):
    ast = parser.parse(program)

    assert ast == [value]


@pytest.mark.parametrize(["program", "value"], CONSTANT_PARAMS)
def test_constant_ws(program, value):
    program = inject_random_ws(f"${program}$", "$")

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


@pytest.mark.parametrize("program", ATOMIC_LITERAL_PARAMS)
def test_atomic_literal_ws(program):
    program_in = inject_random_ws(f"${program}$", "$")

    ast = parser.parse(program_in)

    assert ast == [program]


@pytest.mark.parametrize("program", INVALID_ATOM_PARAMS + ["my$atom"])
def test_invalid_atom(program):
    with pytest.raises(UnexpectedCharacters):
        parser.parse(program)


@pytest.mark.parametrize("program", INVALID_ATOM_PARAMS)
def test_invalid_atom_ws(program):
    program = inject_random_ws(f"${program}$", "$")

    with pytest.raises(UnexpectedCharacters):
        parser.parse(program)


@pytest.mark.parametrize("program", ["1e", "()1e()", "(a b) 4dd", "77x (2 y)", "(5j)"])
def test_consecutive_atoms_require_whitespace(program):
    with pytest.raises(UnexpectedCharacters):
        parser.parse(program)


@pytest.mark.parametrize(["program", "value"], LIST_PARAMS)
def test_list(program, value):
    program = program.replace("$", "")

    ast = parser.parse(program)

    assert ast == [value]


@pytest.mark.parametrize(["program", "value"], LIST_PARAMS)
def test_list_ws(program, value):
    program = inject_random_ws(program, "$")

    ast = parser.parse(program)

    assert ast == [value]


@pytest.mark.parametrize(["program", "value"], PROGRAM_SIMPLE_PARAMS)
def test_program_simple(program, value):
    program = program.replace("$", "")

    ast = parser.parse(program)

    assert ast == value


@pytest.mark.parametrize(["program", "value"], PROGRAM_SIMPLE_PARAMS)
def test_program_simple_ws(program, value):
    program = inject_random_ws(program, "$")

    ast = parser.parse(program)

    assert ast == value


@pytest.mark.parametrize(["program", "value"], PROGRAM_PARAMS)
def test_program(program, value):
    program = program.replace("$", "")

    ast = parser.parse(program)

    assert ast == value


@pytest.mark.parametrize(["program", "value"], PROGRAM_PARAMS)
def test_program_ws(program, value):
    program = inject_random_ws(program, "$")

    ast = parser.parse(program)

    assert ast == value


@pytest.mark.parametrize("program", ["", inject_random_ws("$", "$")])
def test_program_empty(program):
    ast = parser.parse(program)

    assert ast == []


@pytest.mark.parametrize(["program", "value"], LIST_NESTED_PARAMS)
def test_nested_lists(program, value):
    program = program.replace("$", "")

    ast = parser.parse(program)

    assert ast == value


@pytest.mark.parametrize(["program", "value"], LIST_NESTED_PARAMS)
def test_nested_lists_ws(program, value):
    program = inject_random_ws(program, "$")

    ast = parser.parse(program)

    assert ast == value


@pytest.mark.parametrize("program", MISSING_PAREN_PARAMS)
def test_missing_parenthesis(program):
    program = program.replace("$", "")

    with pytest.raises(UnexpectedInput):
        parser.parse(program)


@pytest.mark.parametrize("program", MISSING_PAREN_PARAMS)
def test_missing_parenthesis_ws(program):
    program = inject_random_ws(program, "$")

    with pytest.raises(UnexpectedInput):
        parser.parse(program)
