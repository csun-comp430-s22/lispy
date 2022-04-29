from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from lispyc.sexpression.nodes import Atom
from lispyc.sexpression.nodes import List as ListNode
from lispyc.sexpression.nodes import SExpression
from lispyc.typechecker import types

from .base import Form, FromSExpressionMixin, Node, SpecialForm
from .elementary import Variable

__all__ = (
    "FunctionParameter",
    "Lambda",
    "Define",
    "List",
    "Cons",
    "Car",
    "Cdr",
    "Progn",
    "Set",
    "LetBinding",
    "Let",
    "Branch",
    "Cond",
    "Select",
)


@dataclass(frozen=True, slots=True)
class FunctionParameter(Node, FromSExpressionMixin["FunctionParameter"]):
    """TODO."""

    name: Variable
    type: types.Type

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> FunctionParameter:
        """Parse an `SExpression` into a new `FunctionParameter`."""
        from lispyc.parser import parse_type

        match sexp:
            case ListNode([Atom(str() as name), type_]):
                return cls(Variable(name), parse_type(type_))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Lambda(SpecialForm, id="lambda"):
    """TODO."""

    parameters: Sequence[FunctionParameter]
    body: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Lambda:
        """Parse an `SExpression` into a new `Lambda`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([ListNode(params), body]):
                params = tuple(map(FunctionParameter.from_sexp, params))  # Must be hashable.
                return cls(params, parse_form(body))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Define(SpecialForm, id="define"):
    """TODO."""

    name: Variable
    parameters: Sequence[FunctionParameter]
    body: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Define:
        """Parse an `SExpression` into a new `Define`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([Atom(str() as name), ListNode(params), body]):
                params = tuple(map(FunctionParameter.from_sexp, params))  # Must be hashable.
                return cls(Variable(name), params, parse_form(body))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class List(SpecialForm, id="list"):
    """TODO."""

    elements: Sequence[Form]

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> List:
        """Parse an `SExpression` into a new `List`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode(elements):
                elements = tuple(map(parse_form, elements))  # Must be hashable.
                return cls(elements)
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Cons(SpecialForm, id="cons"):
    """TODO."""

    car: Form
    cdr: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Cons:
        """Parse an `SExpression` into a new `Cons`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([car, cdr]):
                return cls(parse_form(car), parse_form(cdr))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Car(SpecialForm, id="car"):
    """TODO."""

    list: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Car:
        """Parse an `SExpression` into a new `Car`."""
        from lispyc.parser import parse_form

        return cls(parse_form(sexp))


@dataclass(frozen=True, slots=True)
class Cdr(SpecialForm, id="cdr"):
    """TODO."""

    list: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Cdr:
        """Parse an `SExpression` into a new `Cdr`."""
        from lispyc.parser import parse_form

        return cls(parse_form(sexp))


@dataclass(frozen=True, slots=True)
class Progn(SpecialForm, id="progn"):
    """TODO."""

    forms: Sequence[Form]

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Progn:
        """Parse an `SExpression` into a new `Progn`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode(forms):
                forms = tuple(map(parse_form, forms))  # Must be hashable.
                return cls(forms)
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Set(SpecialForm, id="set"):
    """TODO."""

    name: Variable
    value: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Set:
        """Parse an `SExpression` into a new `Set`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([Atom(str() as name), value]):
                return cls(Variable(name), parse_form(value))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class LetBinding(Node, FromSExpressionMixin["LetBinding"]):
    """TODO."""

    name: Variable
    value: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> LetBinding:
        """Parse an `SExpression` into a new `LetBinding`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([Atom(str() as name), value]):
                return cls(Variable(name), parse_form(value))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Let(SpecialForm, id="let"):
    """TODO."""

    bindings: Sequence[LetBinding]
    body: Sequence[Form]

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Let:
        """Parse an `SExpression` into a new `Let`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([ListNode(bindings), ListNode(body)]):
                bindings = tuple(map(LetBinding.from_sexp, bindings))  # Must be hashable.
                body = tuple(map(parse_form, body))  # Must be hashable.
                return cls(bindings, body)
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Branch(Node, FromSExpressionMixin["Branch"]):
    """TODO."""

    predicate: Form
    value: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Branch:
        """Parse an `SExpression` into a new `Branch`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([predicate, value]):
                return cls(parse_form(predicate), parse_form(value))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Cond(SpecialForm, id="cond"):
    """TODO."""

    branches: Sequence[Branch]
    default: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Cond:
        """Parse an `SExpression` into a new `Cond`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([ListNode(branches), default]):
                branches = tuple(map(Branch.from_sexp, branches))  # Must be hashable.
                return cls(branches, parse_form(default))
            case _:
                raise ValueError("Invalid S-expression for special form.")


@dataclass(frozen=True, slots=True)
class Select(SpecialForm, id="select"):
    """TODO."""

    value: Form
    branches: Sequence[Branch]
    default: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Select:
        """Parse an `SExpression` into a new `Select`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListNode([value, ListNode(branches), default]):
                branches = tuple(map(Branch.from_sexp, branches))  # Must be hashable.
                return cls(parse_form(value), branches, parse_form(default))
            case _:
                raise ValueError("Invalid S-expression for special form.")
