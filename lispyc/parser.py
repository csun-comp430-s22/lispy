import lark
from lark import Lark, ast_utils

from lispyc import nodes

__all__ = ("parse",)


class AstTransformer(lark.Transformer):
    """Transform a lispy parse tree (CST) into an AST."""

    SIGNED_INT = int
    FLOAT = float
    LITERAL_ATOM = str

    def BOOL(self, token: lark.Token) -> bool:  # noqa: N802
        """Convert the current token to a Python `bool`."""
        return token == "true"

    def WS(self, _: lark.Token) -> lark.visitors.Discard:  # noqa: N802
        """Discard the current whitespace token."""
        return lark.visitors.Discard


with open("resources/grammar.lark", "r", encoding="utf8") as _f:
    _grammar = _f.read()
    _parser = Lark(_grammar, start="program", propagate_positions=True, maybe_placeholders=False)
    _transformer = ast_utils.create_transformer(nodes, AstTransformer())


def parse(program: str) -> nodes.Program:
    """Parse a lispy program into an AST."""
    tree = _parser.parse(program)
    return _transformer.transform(tree)
