# pyright: reportPrivateImportUsage=false
from typing import Any, cast

import lark
from lark import Lark
from lark.ast_utils import create_transformer  # pyright: ignore [reportUnknownVariableType]

from . import nodes

__all__ = ("parse",)


class AstTransformer(lark.Transformer[lark.Token, nodes.Program]):
    """Transform a lispy parse tree (CST) into an S-expression AST."""

    SIGNED_INT = int
    FLOAT = float
    LITERAL_ATOM = str

    def BOOL(self, token: lark.Token) -> bool:  # noqa: N802
        """Convert the current token to a Python `bool`."""
        return token == "true"

    def WS(self, _: lark.Token) -> Any:  # noqa: N802
        """Discard the current whitespace token."""
        return lark.visitors.Discard


with open("resources/grammar.lark", "r", encoding="utf8") as _f:
    _grammar = _f.read()
    _parser = Lark(_grammar, start="program", propagate_positions=True, maybe_placeholders=False)
    _transformer = cast(AstTransformer, create_transformer(nodes, AstTransformer()))


def parse(program: str) -> nodes.Program:
    """Parse a lispy program into an S-expression AST."""
    tree = _parser.parse(program)
    return _transformer.transform(tree)
