from collections.abc import Sequence
from dataclasses import dataclass

from lispyc.typechecker import types

from .base import Form, Node, SpecialForm
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
class Lambda(SpecialForm, name="lambda"):
    """TODO."""

    parameters: Sequence[FunctionParameter]
    body: Form


@dataclass(frozen=True, slots=True)
class Define(SpecialForm, name="define"):
    """TODO."""

    name: Variable
    parameters: Sequence[FunctionParameter]
    body: Form


@dataclass(frozen=True, slots=True)
class List(SpecialForm, name="list"):
    """TODO."""

    elements: Sequence[Form]


@dataclass(frozen=True, slots=True)
class Cons(SpecialForm, name="cons"):
    """TODO."""

    car: Form
    cdr: Form


@dataclass(frozen=True, slots=True)
class Car(SpecialForm, name="car"):
    """TODO."""

    list: Form


@dataclass(frozen=True, slots=True)
class Cdr(SpecialForm, name="cdr"):
    """TODO."""

    list: Form


@dataclass(frozen=True, slots=True)
class Progn(SpecialForm, name="progn"):
    """TODO."""

    forms: Sequence[Form]


@dataclass(frozen=True, slots=True)
class Set(SpecialForm, name="set"):
    """TODO."""

    name: Variable
    value: Form


@dataclass(frozen=True, slots=True)
class LetBinding(Node):
    """TODO."""

    name: Variable
    value: Form


@dataclass(frozen=True, slots=True)
class Let(SpecialForm, name="let"):
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
class Cond(SpecialForm, name="cond"):
    """TODO."""

    branches: Sequence[Branch]
    default: Form


@dataclass(frozen=True, slots=True)
class Select(SpecialForm, name="select"):
    """TODO."""

    value: Form
    branches: Sequence[Branch]
    default: Form
