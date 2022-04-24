from collections.abc import Sequence
from typing import NamedTuple

__all__ = ("Type", "UnknownType", "IntType", "FloatType", "BoolType", "ListType", "FunctionType")


class Type(NamedTuple):
    """Base class for types that can participate in unification."""


class UnknownType(Type):
    """A type which is currently unknown; a placeholder."""


class IntType(Type):
    """An integer type."""


class FloatType(Type):
    """A floating-point number type."""


class BoolType(Type):
    """A Boolean type (true or false)."""


class ListType(Type):
    """A generic list type."""

    element_type: Type


class FunctionType(Type):
    """A function type."""

    parameter_types: Sequence[Type]
    return_type: Type
