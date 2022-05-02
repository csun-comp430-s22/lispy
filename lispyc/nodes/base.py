from __future__ import annotations

import abc
import typing
from collections.abc import Sequence
from dataclasses import dataclass
from types import MappingProxyType

from lispyc.sexpression.nodes import SExpression
from lispyc.typechecker.types import Type
from lispyc.utils import Abstract, is_redefined_dataclass_with_slots

__all__ = (
    "Node",
    "FromSExpressionMixin",
    "TypeNode",
    "Form",
    "ElementaryForm",
    "ComposedForm",
    "SpecialForm",
    "Program",
)


class Node(Abstract):
    """Base class for all nodes of an abstract syntax tree (AST)."""

    __slots__ = ()


T = typing.TypeVar("T", bound=Node)


class FromSExpressionMixin(typing.Generic[T], metaclass=abc.ABCMeta):
    """Abstract mixin with a classmethod that creates an instance from an `SExpression`."""

    @classmethod
    @abc.abstractmethod
    def from_sexp(cls, sexp: SExpression) -> T:
        """Parse an `SExpression` into a new `Node`."""
        raise NotImplementedError


class TypeNode(Type, Node, abstract=True):
    """Base class for nodes representing types."""

    __slots__ = ()


class Form(Node, abstract=True):
    """Base class for forms - the computational units of lispy."""

    __slots__ = ()


class ElementaryForm(Form, abstract=True):
    """Base class form elementary forms."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class ComposedForm(Form):
    """A composed form - a form consisting of other forms."""

    name: Form
    arguments: Sequence[Form]


class SpecialForm(Form, FromSExpressionMixin["SpecialForm"], metaclass=abc.ABCMeta):
    """Base class for special forms - built-in functions with special evaluation rules.

    The `id` class attribute is required to be set on subclasses. It is the name in lispy that is
    associated with the special form.
    """

    __forms: typing.ClassVar[dict[str, typing.Type[SpecialForm]]] = {}
    id: typing.ClassVar[str]

    def __init_subclass__(cls, /, **kwargs: typing.Any):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "id"):
            # TODO: allow it to be None if subclass is abstract?
            raise ValueError(
                f"The 'id' class attribute must be set on subclasses of {SpecialForm.__name__}."
            )

        if cls.id in cls.__forms and not is_redefined_dataclass_with_slots(
            cls.__forms[cls.id], cls
        ):
            raise ValueError(
                f"A {SpecialForm.__name__} subclass with id {cls.id!r} is already defined."
            )

        cls.__forms[cls.id] = cls

    @classmethod
    @property
    def forms_map(cls) -> MappingProxyType[str, typing.Type[SpecialForm]]:
        """A mapping of registered names to special forms."""
        return MappingProxyType(cls.__forms)


@dataclass(frozen=True, slots=True)
class Program(Node):
    """Top level of a lispy program."""

    body: Sequence[Form]
