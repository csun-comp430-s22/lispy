from collections.abc import Sequence
from dataclasses import dataclass

from lispyc.typechecker import types

from .base import Form, Node
from .elementary import Variable

__all__ = (
    "FunctionParameter",
    "Lambda",
    "Define",
    "List",
    "Cons",
    "Car",
    "Cdr",
    "Progn",
    "Set",
    "LetBinding",
    "Let",
    "Branch",
    "Cond",
    "Select",
)


@dataclass(frozen=True, slots=True)
class FunctionParameter(Node):
    """TODO."""

    name: Variable
    type: types.Type


@dataclass(frozen=True, slots=True)
class Lambda(Form):
    """TODO."""

    parameters: Sequence[FunctionParameter]
    body: Form


@dataclass(frozen=True, slots=True)
class Define(Form):
    """TODO."""

    name: Variable
    parameters: Sequence[FunctionParameter]
    body: Form


@dataclass(frozen=True, slots=True)
class List(Form):
    """TODO."""

    elements: Sequence[Form]


@dataclass(frozen=True, slots=True)
class Cons(Form):
    """TODO."""

    car: Form
    cdr: Form


@dataclass(frozen=True, slots=True)
class Car(Form):
    """TODO."""

    list: Form


@dataclass(frozen=True, slots=True)
class Cdr(Form):
    """TODO."""

    list: Form


@dataclass(frozen=True, slots=True)
class Progn(Form):
    """TODO."""

    forms: Sequence[Form]


@dataclass(frozen=True, slots=True)
class Set(Form):
    """TODO."""

    name: Variable
    value: Form


@dataclass(frozen=True, slots=True)
class LetBinding(Node):
    """TODO."""

    name: Variable
    value: Form


@dataclass(frozen=True, slots=True)
class Let(Form):
    """TODO."""

    name: Variable
    value: Sequence[LetBinding]
    body: Sequence[Form]


@dataclass(frozen=True, slots=True)
class Branch(Node):
    """TODO."""

    predicate: Form
    value: Form


@dataclass(frozen=True, slots=True)
class Cond(Form):
    """TODO."""

    branches: Sequence[Branch]
    default: Form


@dataclass(frozen=True, slots=True)
class Select(Form):
    """TODO."""

    value: Form
    branches: Sequence[Branch]
    default: Form
