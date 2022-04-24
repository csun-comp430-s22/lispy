import abc
from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ("Type", "UnknownType", "IntType", "FloatType", "BoolType", "ListType", "FunctionType")


class Type(metaclass=abc.ABCMeta):
    """Base class for types that can participate in unification."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class UnknownType(Type):
    """A type which is currently unknown; a placeholder."""


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
