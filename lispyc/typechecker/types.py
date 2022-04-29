from dataclasses import dataclass
from typing import Any

from lispyc.utils import Abstract

__all__ = ("Type", "UnknownType", "TypeVarType")


class Type(Abstract):
    """Base class for types that can participate in unification."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class UnknownType(Type):
    """A type which is currently unknown; a placeholder."""

    def __eq__(self, other: Any) -> bool:
        return self is other


@dataclass(frozen=True, slots=True)
class TypeVarType(Type):
    """A type variable type. Used for implementing generic special forms."""
