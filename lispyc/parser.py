from lispyc import exceptions, nodes, sexpression
from lispyc.exceptions import TypeSyntaxError
from lispyc.sexpression import Atom, List, Program, SExpression

__all__ = ("parse", "parse_form", "parse_program", "parse_type")


def parse(program: str) -> nodes.Program:
    """Parse a lispy program into an AST."""
    program_node = sexpression.parse(program)
    return parse_program(program_node)


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
            arguments = tuple(map(parse_form, forms))
            return nodes.ComposedForm(name, arguments)
        case List([]):
            return nodes.List(())  # It's nil.
        case _:  # pragma: no cover
            # Precaution; unreachable in practice because the match is (currently) exhaustive.
            raise exceptions.SyntaxError("Invalid syntax: unknown form for S-expression")


def parse_program(program: Program) -> nodes.Program:
    """Parse the `SExpression`s in a `Program` into `Form`s."""
    body = tuple(map(parse_form, program.body))
    return nodes.Program(body)


def parse_type(type_: SExpression) -> nodes.Type:
    """Parse an `SExpression` into a `Type`."""
    match type_:
        case Atom("int"):
            return nodes.IntType()
        case Atom("float"):
            return nodes.FloatType()
        case Atom("bool"):
            return nodes.BoolType()
        case List([Atom("list"), list_type]):
            return nodes.ListType(parse_type(list_type))
        case List([Atom("func"), List(param_types), return_type]):
            return_type = parse_type(return_type)
            param_types = tuple(map(parse_type, param_types))
            return nodes.FunctionType(param_types, return_type)
        case List([Atom("list"), *_]):
            raise TypeSyntaxError.from_syntax("list", "<type>")
        case List([Atom("func"), *_]):
            raise TypeSyntaxError.from_syntax("type", "'(' <type>* ')' <type>")
        case _:
            raise TypeSyntaxError("Invalid syntax: unknown type for S-expression")
