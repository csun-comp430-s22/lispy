from collections.abc import MutableMapping

from lispyc import nodes
from lispyc.nodes import Constant, Form, Program, SpecialForm, Variable
from lispyc.nodes.types import BoolType, FloatType, IntType, ListType

from .types import Type, UnknownType
from .unifier import Unifier

__all__ = ("TypeChecker",)

Scope = MutableMapping[Variable, Type]

NIL = "nil"


class TypeChecker:
    """Enforce type safety - that there are no discrepancies between expected and actual types."""

    def __init__(self, program: Program):
        self._program = program
        self._unifier = Unifier()

    @classmethod
    def assert_program_valid(cls, program: Program) -> None:
        """Typecheck `program` and raise an error if it fails."""
        checker = cls(program)
        global_scope = {}

        for form in program.body:
            checker.check_form(form, global_scope)

    def check_form(self, form: Form, scope: Scope) -> Type:
        """Typecheck a `Form` and return its type."""
        match form:
            case Constant(int()):
                return IntType()
            case Constant(float()):
                return FloatType()
            case Constant(bool()):
                return BoolType()
            case nodes.List() as list_:
                return self._check_list(list_, scope)
            case nodes.Set(variable, value):
                return self._bind(variable, value, scope)
            case _:
                raise ValueError(f"Unknown form {form!r}.")

    def _bind(self, variable: Variable, value: Form, scope: Scope) -> Type:
        """Bind or rebind a variable in the given `scope` and return the type of its new value.

        The variable's name must not be the name of a special form or "nil".
        """
        if variable.name in SpecialForm.forms_map:
            raise ValueError(
                f"Cannot bind to name {variable.name!r}: rebinding special forms is disallowed."
            )

        if variable.name == NIL:
            raise ValueError(
                f"Cannot bind to name {variable.name!r}: rebinding {NIL!r} is disallowed."
            )

        type_ = self.check_form(value, scope)
        if variable in scope:
            self._unifier.unify(scope[variable], type_)

        scope[variable] = type_

        return type_

    def _check_list(self, list_: nodes.List, scope: Scope) -> ListType:
        """Typecheck a `List` and return its type.

        The list must be homogeneous i.e. its elements must all have the same type.
        """
        if not list_.elements:
            return ListType(UnknownType())  # It's nil.

        # Get the type of the first element.
        elements_iter = iter(list_.elements)
        first_type = self.check_form(next(elements_iter), scope)

        # Unify all elements - the list must be homogeneous.
        for element in elements_iter:
            current_type = self.check_form(element, scope)

            # TODO: raise more specific error about list not being homogeneous.
            # Currently, the unifier's errors are too vague to be able to do this.
            self._unifier.unify(first_type, current_type)

        return ListType(first_type)
