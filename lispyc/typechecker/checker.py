from lispyc import nodes
from lispyc.nodes import Constant, Form, Program
from lispyc.nodes.types import BoolType, FloatType, IntType, ListType

from .types import Type, UnknownType
from .unifier import Unifier

__all__ = ("TypeChecker",)


class TypeChecker:
    """Enforce type safety - that there are no discrepancies between expected and actual types."""

    def __init__(self, program: Program):
        self._program = program
        self._unifier = Unifier()

    @classmethod
    def assert_program_valid(cls, program: Program) -> None:
        """Typecheck `program` and raise an error if it fails."""
        checker = cls(program)
        for form in program.body:
            checker.check_form(form)

    def check_form(self, form: Form) -> Type:
        """Typecheck a `Form` and return its type."""
        match form:
            case Constant(int()):
                return IntType()
            case Constant(float()):
                return FloatType()
            case Constant(bool()):
                return BoolType()
            case nodes.List() as list_:
                return self._check_list(list_)
            case _:
                raise ValueError(f"Unknown form {form!r}.")

    def _check_list(self, list_: nodes.List) -> ListType:
        """Typecheck a `List` and return its type.

        The list must be homogeneous i.e. its elements must all have the same type.
        """
        if not list_.elements:
            return ListType(UnknownType())  # It's nil.

        # Get the type of the first element.
        elements_iter = iter(list_.elements)
        first_type = self.check_form(next(elements_iter))

        # Unify all elements - the list must be homogeneous.
        for element in elements_iter:
            current_type = self.check_form(element)

            # TODO: raise more specific error about list not being homogeneous.
            # Currently, the unifier's errors are too vague to be able to do this.
            self._unifier.unify(first_type, current_type)

        return ListType(first_type)
