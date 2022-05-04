import copy
from collections.abc import Iterable, MutableMapping

from lispyc import exceptions, nodes
from lispyc.nodes import ComposedForm, Constant, Form, Program, SpecialForm, Variable
from lispyc.nodes.types import BoolType, FloatType, FunctionType, IntType, ListType

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
        """Typecheck `program` and raise LispyError if it fails."""
        checker = cls(program)
        global_scope = {}

        for form in program.body:
            checker.check_form(form, global_scope)

    def check_form(self, form: Form, scope: Scope) -> Type:
        """Typecheck a `Form` and return its type."""
        match form:
            case Constant(bool()):
                return BoolType()
            case Constant(int()):
                return IntType()
            case Constant(float()):
                return FloatType()
            case Variable() as variable:
                return self._get_binding(variable, scope)
            case ComposedForm() as form:
                return self._check_composed_form(form, scope)
            case nodes.Lambda() as lambda_:
                return self._check_lambda(lambda_, scope)
            case nodes.List() as list_:
                return self._check_list(list_, scope)
            case nodes.Cons() as cons:
                return self._check_cons(cons, scope)
            case nodes.Car() as car:
                return self._check_car(car, scope)
            case nodes.Cdr() as cdr:
                return self._check_cdr(cdr, scope)
            case nodes.Progn() as progn:
                return self._check_progn(progn, scope)
            case nodes.Set(variable, value):
                return self._bind(variable, value, scope)
            case nodes.Let() as let:
                return self._check_let(let, scope)
            case nodes.Cond() as cond:
                return self._check_cond(cond, scope)
            case nodes.Select() as select:
                return self._check_select(select, scope)
            case _:
                raise TypeError(f"Unknown form {form!r}.")

    def _assert_name_valid(self, name: str) -> None:
        """Raise InvalidNameError if `name` is not allowed to be rebound."""
        if name in SpecialForm.forms_map:
            raise exceptions.InvalidNameError(
                f"Cannot bind to name {name!r}: rebinding special forms is disallowed", name
            )

        if name == NIL:
            raise exceptions.InvalidNameError(
                f"Cannot bind to name {name!r}: rebinding {NIL!r} is disallowed", name
            )

    def _bind(self, variable: Variable, value: Form, scope: Scope) -> Type:
        """Bind or rebind a variable in the given `scope` and return the type of its new value.

        The variable's name must not be the name of a special form or "nil".
        """
        self._assert_name_valid(variable.name)

        if variable not in scope:
            raise exceptions.UnboundNameError(
                f"Cannot bind to name {variable.name!r}: name is not in scope", variable.name
            )

        type_ = self.check_form(value, scope)
        self._unifier.unify(scope[variable], type_)

        return type_

    def _check_car(self, car: nodes.Car, scope: Scope) -> Type:
        """Typecheck a `Car` and return the type of the list element it returns."""
        type_ = self.check_form(car.list, scope)
        element_type = UnknownType()
        expected_type = ListType(element_type)

        self._unifier.unify(type_, expected_type)

        return element_type

    def _check_cdr(self, cdr: nodes.Cdr, scope: Scope) -> ListType:
        """Typecheck a `Cdr` and return the type of the list it returns."""
        type_ = self.check_form(cdr.list, scope)
        expected_type = ListType(UnknownType())

        self._unifier.unify(type_, expected_type)

        return expected_type

    def _check_composed_form(self, form: ComposedForm, scope: Scope) -> Type:
        """Typecheck a `ComposedForm` and return the called function's return type."""
        param_types = tuple(self.check_form(arg, scope) for arg in form.arguments)
        expected_type = FunctionType(param_types, UnknownType())
        current_type = self.check_form(form.name, scope)

        self._unifier.unify(current_type, expected_type)

        return expected_type.return_type

    def _check_cond(self, cond: nodes.Cond, scope: Scope) -> Type:
        """Typecheck a `Cond` and return its type."""
        branches_iter = iter(cond.branches)
        first_branch = next(branches_iter)

        first_predicate_type = self.check_form(first_branch.predicate, scope)
        self._unifier.unify(first_predicate_type, BoolType())

        first_value_type = self.check_form(first_branch.value, scope)

        for branch in branches_iter:
            predicate_type = self.check_form(branch.predicate, scope)
            self._unifier.unify(first_predicate_type, predicate_type)

            value_type = self.check_form(branch.value, scope)
            self._unifier.unify(first_value_type, value_type)

        default_type = self.check_form(cond.default, scope)
        self._unifier.unify(first_value_type, default_type)

        return default_type

    def _check_cons(self, cons: nodes.Cons, scope: Scope) -> ListType:
        """Typecheck a `Cons` and return the type of the list it returns."""
        car_type = self.check_form(cons.car, scope)
        cdr_type = self.check_form(cons.cdr, scope)

        cdr_element_type = UnknownType()
        expected_cdr_type = ListType(cdr_element_type)

        self._unifier.unify(cdr_type, expected_cdr_type)
        self._unifier.unify(car_type, cdr_element_type)

        return expected_cdr_type

    def _check_lambda(self, lambda_: nodes.Lambda, scope: Scope) -> FunctionType:
        """Typecheck a `Lambda` and return its type.

        Raise DuplicateNameError if there is a duplicate name in the lambda's parameters.
        """
        try:
            func_scope = self._create_scope(lambda_.parameters, scope)
        except exceptions.DuplicateNameError as e:
            raise exceptions.DuplicateNameError(
                f"Invalid syntax for special form lambda: duplicate parameter name {e.name!r}",
                e.name,
            )

        param_types = tuple(param.type for param in lambda_.parameters)
        return_type = self.check_form(lambda_.body, func_scope)

        return FunctionType(param_types, return_type)

    def _check_let(self, let: nodes.Let, scope: Scope) -> Type:
        """Typecheck a `Let` and return the type of its body's last form."""
        # Create FunctionParameters because it's a convenient data structure for storing pairs
        # of variables and types, which is what _create_scope() needs.
        params = [
            nodes.FunctionParameter(b.name, self.check_form(b.value, scope)) for b in let.bindings
        ]

        try:
            let_scope = self._create_scope(params, scope)
        except exceptions.DuplicateNameError as e:
            raise exceptions.DuplicateNameError(
                f"Invalid syntax for special form let: duplicate binding name {e.name!r}", e.name
            )

        # let's body has the same behaviour as progn, except let uses a new scope.
        progn = nodes.Progn(let.body)

        return self._check_progn(progn, let_scope)

    def _check_list(self, list_: nodes.List, scope: Scope) -> ListType:
        """Typecheck a `List` and return its type.

        Raise TypeError if the list is not homogeneous.
        """
        if not list_.elements:
            return ListType(UnknownType())  # It's nil.

        # Get the type of the first element.
        elements_iter = iter(list_.elements)
        first_type = self.check_form(next(elements_iter), scope)

        # Unify all elements - the list must be homogeneous.
        for i, element in enumerate(elements_iter, 1):
            current_type = self.check_form(element, scope)

            try:
                self._unifier.unify(first_type, current_type)
            except exceptions.UnificationError:
                raise exceptions.TypeError(
                    "List is not homogeneous: "
                    f"expected type {first_type} but got {current_type} for element {i}"
                )

        return ListType(first_type)

    def _check_progn(self, progn: nodes.Progn, scope: Scope) -> Type:
        """Typecheck a `Progn` and return the type of its last form."""
        type_ = None
        for form in progn.forms:
            type_ = self.check_form(form, scope)

        # TODO: In practice the parser requires > 0 forms for Progn and Let, but I'm still scared.
        assert type_ is not None

        return type_

    def _check_select(self, select: nodes.Select, scope: Scope) -> Type:
        """Typecheck a `Select` and return its type."""
        select_value_type = self.check_form(select.value, scope)
        self._unifier.unify(select_value_type, UnknownType())

        default_type = self.check_form(select.default, scope)

        for branch in select.branches:
            predicate_type = self.check_form(branch.predicate, scope)
            self._unifier.unify(select_value_type, predicate_type)

            value_type = self.check_form(branch.value, scope)
            self._unifier.unify(default_type, value_type)

        return default_type

    def _create_scope(self, parameters: Iterable[nodes.FunctionParameter], scope: Scope) -> Scope:
        """Return a new nested scope from an outer `scope` with the given `parameters` in scope.

        Raise DuplicateNameError if there is a duplicate name in `parameters`.
        """
        names: set[str] = set()
        nested_scope = copy.copy(scope)

        for param in parameters:
            self._assert_name_valid(param.name.name)
            if param.name.name in names:
                raise exceptions.DuplicateNameError(
                    f"Invalid syntax: duplicate name {param.name.name!r}", param.name.name
                )

            names.add(param.name.name)

            # TODO: show warning if name shadows same name in outer scope.
            nested_scope[param.name] = param.type

        return nested_scope

    def _get_binding(self, variable: Variable, scope: Scope) -> Type:
        """Get the type of the value bound to the given `variable` in the given `scope`.

        Raise UnboundNameError if the name is not in scope.
        """
        if variable.name == NIL:
            # nil is a special case that's always in scope.
            # Just like in _check_list, each reference to nil must return a new instance of the type
            # to prevent nils referenced in different scopes from unifying with each other.
            return ListType(UnknownType())
        elif variable in scope:
            return scope[variable]
        else:
            raise exceptions.UnboundNameError(
                f"Cannot retrieve binding {variable.name!r}: name is not in scope", variable.name
            )
