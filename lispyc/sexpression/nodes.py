from dataclasses import dataclass
from typing import Any

import lark
from lark import ast_utils

from lispyc.utils import Abstract, MatchExclusionsMeta

__all__ = ("Node", "SExpression", "Atom", "List", "Program")


@dataclass(frozen=True, slots=True)
class Node(
    ast_utils.Ast, ast_utils.WithMeta, Abstract, metaclass=MatchExclusionsMeta, exclude={"meta"}
):
    """Base class for all nodes of an abstract syntax tree (AST)."""

    meta: lark.tree.Meta


class SExpression(Node, abstract=True):
    """A symbolic expression. The fundamental syntactic element of lispy."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class Atom(SExpression):
    """An atomic S-expression; an atomic literal or a constant.

    `value` contains the Python object the constant represents.
    If the atom is instead an atomic literal, then it's a string representing the atom's name.
    """

    value: str | int | float | bool

    def __eq__(self, other: Any) -> bool:  # pragma: no cover
        if isinstance(other, Atom):
            return self.value == other.value
        else:
            return self.value == other


@dataclass(frozen=True, slots=True)
class List(SExpression, ast_utils.AsList):
    """An S-expression list.

    `elements` holds a list of zero or more nodes representing the list's elements.
    They are S-expressions which are contained within the list.
    """

    elements: list[SExpression]

    def __eq__(self, other: Any) -> bool:  # pragma: no cover
        if isinstance(other, List):
            return self.elements == other.elements
        else:
            return self.elements == other


@dataclass(frozen=True, slots=True)
class Program(Node, ast_utils.AsList):
    """The top level of a lispy program.

    `body` holds a list of zero or more direct child nodes.
    They are S-expressions which are at the top level of the program.
    """

    body: list[SExpression]

    def __eq__(self, other: Any) -> bool:  # pragma: no cover
        if isinstance(other, Program):
            return self.body == other.body
        else:
            return self.body == other
