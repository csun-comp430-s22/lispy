from dataclasses import dataclass

from .base import ElementaryForm

__all__ = ("Constant", "Variable")


@dataclass(frozen=True, slots=True)
class Constant(ElementaryForm):
    """A literal value."""

    value: int | float | bool


@dataclass(frozen=True, slots=True)
class Variable(ElementaryForm):
    """An atomic literal which is an identifier for some associated value."""

    name: str
