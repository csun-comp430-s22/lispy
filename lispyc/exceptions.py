from __future__ import annotations

from typing import NoReturn


class LispyError(Exception):
    """Base class for all lispy compiler exceptions."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class SyntaxError(LispyError):
    """Raised when a syntax error is encountered."""


class SpecialFormSyntaxError(SyntaxError):
    """Raised when a syntax error is encountered for a special form."""

    @classmethod
    def from_syntax(cls, name: str, inner_syntax: str) -> SpecialFormSyntaxError:
        """Return a new `SpecialFormSyntaxError` with a message showing expected syntax."""
        return cls(
            f"Invalid syntax for special form {name}: expected '(' '{name}' {inner_syntax} ')'"
        )


class DuplicateNameError(SpecialFormSyntaxError):
    """Raised when a function has a duplicate parameter name or a let has a duplicate name."""

    def __init__(self, message: str, name: str):
        super().__init__(message)
        self.message = message
        self.name = name

    @classmethod
    def from_syntax(cls, name: str, inner_syntax: str) -> NoReturn:
        """Not implemented."""
        raise NotImplementedError


class TypeSyntaxError(SyntaxError):
    """Raised when the parser encounters a syntax error for a type."""

    @classmethod
    def from_syntax(cls, name: str, inner_syntax: str) -> TypeSyntaxError:
        """Return a new `TypeSyntaxError` with a message showing expected syntax."""
        return cls(f"Invalid syntax for type {name}: expected '(' '{name}' {inner_syntax} ')'")


class TypeError(LispyError):
    """Raised when typechecking fails on a form."""


class UnificationError(TypeError):
    """Raised when unifying types fails."""


class CyclicTypeError(TypeError):
    """Raised when unifying types which refer to each other."""


class BindingError(LispyError):
    """Raised when a binding-related error occurs."""

    def __init__(self, message: str, name: str):
        super().__init__(message)
        self.message = message
        self.name = name


class InvalidNameError(BindingError):
    """Raised when attempting to bind to a disallowed name."""


class UnboundNameError(BindingError):
    """Raised when referencing a name that is unbound (i.e. not in scope)."""
