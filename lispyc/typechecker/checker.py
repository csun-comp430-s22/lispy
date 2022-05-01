from lispyc.nodes import Constant, Form, Program
from lispyc.nodes.types import BoolType, FloatType, IntType

from .types import Type

__all__ = ("TypeChecker",)


class TypeChecker:
    """Enforce type safety - that there are no discrepancies between expected and actual types."""

    def __init__(self, program: Program):
        self._program = program

    def check_form(self, form: Form) -> Type:
        """Typecheck a `Form` and return its type."""
        match form:
            case Constant(int()):
                return IntType()
            case Constant(float()):
                return FloatType()
            case Constant(bool()):
                return BoolType()
            case _:
                raise ValueError(f"Unknown form {form!r}.")
