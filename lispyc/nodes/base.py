import abc
from collections.abc import Sequence
from dataclasses import dataclass

from lispyc.typechecker.types import Type

__all__ = ("Node", "TypeNode", "Form", "ElementaryForm", "ComposedForm", "SpecialForm", "Program")


class Node(metaclass=abc.ABCMeta):
    """Base class for all nodes of an abstract syntax tree (AST)."""

    __slots__ = ()


class TypeNode(Type, Node, metaclass=abc.ABCMeta):
    """Base class for nodes representing types."""

    __slots__ = ()


class Form(Node, metaclass=abc.ABCMeta):
    """Base class for forms - the computational units of lispy."""

    __slots__ = ()


class ElementaryForm(Form, metaclass=abc.ABCMeta):
    """Base class form elementary forms."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class ComposedForm(Form):
    """A composed form - a form consisting of other forms."""

    name: Form
    arguments: Sequence[Form]


class SpecialForm(Form, metaclass=abc.ABCMeta):
    """Base class for special forms - built-in functions with special evaluation rules."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class Program(Node):
    """Top level of a lispy program."""

    body: Sequence[Form]
