from lispyc import nodes
from lispyc.sexpression.nodes import Atom, List, SExpression


def _parse_type(type_: SExpression) -> nodes.TypeNode:
    """Parse an `SExpression` into a `TypeNode`."""
    match type_:
        case Atom("int"):
            return nodes.IntType()
        case Atom("float"):
            return nodes.FloatType()
        case Atom("bool"):
            return nodes.BoolType()
        case List([Atom("list"), list_type]):
            return nodes.ListType(_parse_type(list_type))
        case List([Atom("func"), *param_types, return_type]):
            parsed_params = []
            for param_type in param_types:
                parsed_params.append(_parse_type(param_type))

            # The parameter_types sequence must be hashable. Thus, convert it to a tuple.
            return nodes.FunctionType(tuple(parsed_params), _parse_type(return_type))
        case _:
            raise ValueError("Unknown type or invalid format for type.")
