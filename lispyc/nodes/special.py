from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from lispyc.exceptions import SpecialFormSyntaxError
from lispyc.sexpression import Atom
from lispyc.sexpression import List as ListSExp
from lispyc.sexpression import SExpression

from .base import Form, FromSExpressionMixin, Node, SpecialForm, Type
from .elementary import Variable

__all__ = (
    "FunctionParameter",
    "Lambda",
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
    type: Type

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> FunctionParameter:
        """Parse an `SExpression` into a new `FunctionParameter`."""
        from lispyc.parser import parse_type

        match sexp:
            case ListSExp([Atom(str() as name), type_]):
                return cls(Variable(name), parse_type(type_))
            case _:
                raise SpecialFormSyntaxError(
                    "Invalid syntax for function parameter: expected '(' <name> <type> ')'"
                )


@dataclass(frozen=True, slots=True)
class Lambda(SpecialForm):
    """TODO."""

    id = "lambda"
    parameters: Sequence[FunctionParameter]
    body: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Lambda:
        """Parse an `SExpression` into a new `Lambda`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, ListSExp(params), body]):
                assert id_ == cls.id
                params = tuple(map(FunctionParameter.from_sexp, params))
                return cls(params, parse_form(body))
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "'(' <func-param>* ')' <form>")


@dataclass(frozen=True, slots=True)
class List(SpecialForm):
    """TODO."""

    id = "list"
    elements: Sequence[Form]

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> List:
        """Parse an `SExpression` into a new `List`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, *elements]):
                assert id_ == cls.id
                elements = tuple(map(parse_form, elements))
                return cls(elements)
            case _:  # pragma: no cover
                # Unreachable in practice because parse_form already matched the same case before
                # calling this from_sexp.
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<form>*")


@dataclass(frozen=True, slots=True)
class Cons(SpecialForm):
    """TODO."""

    id = "cons"
    car: Form
    cdr: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Cons:
        """Parse an `SExpression` into a new `Cons`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, car, cdr]):
                assert id_ == cls.id
                return cls(parse_form(car), parse_form(cdr))
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<form> <form>")


@dataclass(frozen=True, slots=True)
class Car(SpecialForm):
    """TODO."""

    id = "car"
    list: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Car:
        """Parse an `SExpression` into a new `Car`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, list_]):
                assert id_ == cls.id
                return cls(parse_form(list_))
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<form>")


@dataclass(frozen=True, slots=True)
class Cdr(SpecialForm):
    """TODO."""

    id = "cdr"
    list: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Cdr:
        """Parse an `SExpression` into a new `Cdr`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, list_]):
                assert id_ == cls.id
                return cls(parse_form(list_))
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<form>")


@dataclass(frozen=True, slots=True)
class Progn(SpecialForm):
    """TODO."""

    id = "progn"
    forms: Sequence[Form]

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Progn:
        """Parse an `SExpression` into a new `Progn`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, form_1, form_2, *forms]):
                assert id_ == cls.id
                forms = tuple(map(parse_form, [form_1, form_2] + forms))
                return cls(forms)
            case _:  # pragma: no cover
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<form> <form>+")


@dataclass(frozen=True, slots=True)
class Set(SpecialForm):
    """TODO."""

    id = "set"
    name: Variable
    value: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Set:
        """Parse an `SExpression` into a new `Set`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, Atom(str() as name), value]):
                assert id_ == cls.id
                return cls(Variable(name), parse_form(value))
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<name> <form>")


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
            case ListSExp([Atom(str() as name), value]):
                return cls(Variable(name), parse_form(value))
            case _:
                raise SpecialFormSyntaxError(
                    "Invalid syntax for let binding: expected '(' <name> <form> ')'"
                )


@dataclass(frozen=True, slots=True)
class Let(SpecialForm):
    """TODO."""

    id = "let"
    bindings: Sequence[LetBinding]
    body: Sequence[Form]

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Let:
        """Parse an `SExpression` into a new `Let`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, ListSExp([binding, *bindings]), body_1, *body_rest]):
                assert id_ == cls.id
                bindings = tuple(map(LetBinding.from_sexp, [binding] + bindings))
                body = tuple(map(parse_form, [body_1] + body_rest))
                return cls(bindings, body)
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "'(' <let-binding>+ ')' <form>+")


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
            case ListSExp([predicate, value]):
                return cls(parse_form(predicate), parse_form(value))
            case _:
                raise SpecialFormSyntaxError(
                    "Invalid syntax for branch: expected '(' <form> <value> ')'"
                )


@dataclass(frozen=True, slots=True)
class Cond(SpecialForm):
    """TODO."""

    id = "cond"
    branches: Sequence[Branch]
    default: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Cond:
        """Parse an `SExpression` into a new `Cond`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, branch, *branches, default]):
                assert id_ == cls.id
                branches = tuple(map(Branch.from_sexp, [branch] + branches))
                return cls(branches, parse_form(default))
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<branch>+ <form>")


@dataclass(frozen=True, slots=True)
class Select(SpecialForm):
    """TODO."""

    id = "select"
    value: Form
    branches: Sequence[Branch]
    default: Form

    @classmethod
    def from_sexp(cls, sexp: SExpression) -> Select:
        """Parse an `SExpression` into a new `Select`."""
        from lispyc.parser import parse_form

        match sexp:
            case ListSExp([id_, value, branch, *branches, default]):
                assert id_ == cls.id
                branches = tuple(map(Branch.from_sexp, [branch] + branches))
                return cls(parse_form(value), branches, parse_form(default))
            case _:
                raise SpecialFormSyntaxError.from_syntax(cls.id, "<form> <branch>+ <form>")
