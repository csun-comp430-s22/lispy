from lispyc import nodes
from lispyc.sexpression.nodes import Atom, List, SExpression

__all__ = ("parse_form", "parse_type")


def parse_form(form: SExpression) -> nodes.Form:
    """Parse an `SExpression` into a `Form`."""
    match form:
        case Atom(str() as value):
            return nodes.Variable(value)
        case Atom(int() | float() | bool() as value):
            return nodes.Constant(value)
        case List([Atom(str() as name), *_]) if name in nodes.SpecialForm.forms_map:
            return nodes.SpecialForm.forms_map[name].from_sexp(form)
        case List([name, *forms]):
            name = parse_form(name)
            arguments = tuple(map(parse_form, forms))  # Must be hashable.
            return nodes.ComposedForm(name, arguments)
        case _:
            raise ValueError(f"Unknown form for S-expression {form}.")


def parse_type(type_: SExpression) -> nodes.TypeNode:
    """Parse an `SExpression` into a `TypeNode`."""
    match type_:
        case Atom("int"):
            return nodes.IntType()
        case Atom("float"):
            return nodes.FloatType()
        case Atom("bool"):
            return nodes.BoolType()
        case List([Atom("list"), list_type]):
            return nodes.ListType(parse_type(list_type))
        case List([Atom("func"), *param_types, return_type]):
            return_type = parse_type(return_type)
            param_types = tuple(map(parse_type, param_types))  # Must be hashable.
            return nodes.FunctionType(param_types, return_type)
        case _:
            raise ValueError("Unknown type or invalid format for type.")
