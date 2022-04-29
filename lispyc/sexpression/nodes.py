from dataclasses import dataclass
from typing import Any

import lark
from lark import ast_utils

from lispyc.utils import Abstract

__all__ = ("Node", "SExpression", "Atom", "List", "Program")


class Node(ast_utils.Ast, Abstract):
    """Base class for all nodes of an abstract syntax tree (AST)."""


@dataclass
class SExpression(Node, ast_utils.WithMeta, abstract=True):
    """A symbolic expression. The fundamental syntactic element of lispy."""

    meta: lark.tree.Meta


@dataclass
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


@dataclass
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


@dataclass
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
