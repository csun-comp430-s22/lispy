from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .base import Type

__all__ = ("IntType", "FloatType", "BoolType", "ListType", "FunctionType", "UnknownType")


@dataclass(frozen=True, slots=True)
class IntType(Type):
    """An integer type."""


@dataclass(frozen=True, slots=True)
class FloatType(Type):
    """A floating-point number type."""


@dataclass(frozen=True, slots=True)
class BoolType(Type):
    """A Boolean type (true or false)."""


@dataclass(frozen=True, slots=True)
class ListType(Type):
    """A generic list type."""

    element_type: Type


@dataclass(frozen=True, slots=True)
class FunctionType(Type):
    """A function type."""

    parameter_types: Sequence[Type]
    return_type: Type


@dataclass(frozen=True, slots=True)
class UnknownType(Type):
    """A type which is currently unknown; a placeholder."""

    def __eq__(self, other: Any) -> bool:
        return self is other
