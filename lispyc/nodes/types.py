from collections.abc import Sequence
from dataclasses import dataclass

from lispyc.typechecker.types import Type

from .base import TypeNode

__all__ = ("IntType", "FloatType", "BoolType", "ListType", "FunctionType")


@dataclass(frozen=True, slots=True)
class IntType(TypeNode):
    """An integer type."""


@dataclass(frozen=True, slots=True)
class FloatType(TypeNode):
    """A floating-point number type."""


@dataclass(frozen=True, slots=True)
class BoolType(TypeNode):
    """A Boolean type (true or false)."""


@dataclass(frozen=True, slots=True)
class ListType(TypeNode):
    """A generic list type."""

    element_type: Type


@dataclass(frozen=True, slots=True)
class FunctionType(TypeNode):
    """A function type."""

    parameter_types: Sequence[Type]
    return_type: Type
