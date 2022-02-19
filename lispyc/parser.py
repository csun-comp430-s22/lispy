import lark
from lark import Lark, ast_utils

from lispyc import nodes

__all__ = ("parse",)


class AstTransformer(lark.Transformer):
    """Transform a lispy parse tree (CST) into an AST."""

    SIGNED_INT = int
    FLOAT = float
    BOOL = bool
    LITERAL_ATOM = str

    def WS(self, _: lark.Token) -> lark.visitors.Discard:  # noqa: N802
        """Discard the current whitespace token."""
        return lark.visitors.Discard


def parse(program: str) -> nodes.Program:
    """Parse a lispy program into an AST."""
    with open("resources/grammar.lark", "r", encoding="utf8") as f:
        grammar = f.read()

    parser = Lark(grammar, start="program")
    transformer = ast_utils.create_transformer(nodes, AstTransformer())

    tree = parser.parse(program)

    return transformer.transform(tree)
