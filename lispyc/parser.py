import lark
from lark import Lark, Transformer

__all__ = ("parse",)


class DiscardWhitespace(Transformer):
    """Discard all whitespace tokens in a tree."""

    def WS(self, _: lark.Token) -> lark.visitors.Discard:  # noqa: N802
        """Discard the current whitespace token."""
        return lark.visitors.Discard


def parse(program: str) -> lark.Tree[lark.Token]:
    """Parse a lispy program into a parse tree."""
    with open("resources/grammar.lark", "r", encoding="utf8") as f:
        grammar = f.read()

    parser = Lark(grammar, start="program")
    tree = parser.parse(program)

    return DiscardWhitespace().transform(tree)
