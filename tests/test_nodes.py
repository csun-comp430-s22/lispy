from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from lispyc import nodes
from lispyc.sexpression.nodes import SExpression

ABSTRACT_NODE_PARAMS = [
    nodes.Node,
    nodes.FromSExpressionMixin,
    nodes.TypeNode,
    nodes.Form,
    nodes.ElementaryForm,
    nodes.SpecialForm,
]


def test_from_sexp_abc_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        nodes.FromSExpressionMixin.from_sexp(MagicMock(spec_set=SExpression))


@pytest.mark.parametrize("type_", ABSTRACT_NODE_PARAMS)
def test_abstract_node_instantiation_raises_type_error(type_):
    with pytest.raises(TypeError):
        type_()


def test_special_form_missing_id_raises_value_error():
    with pytest.raises(ValueError, match="must be set"):

        class Child1(nodes.SpecialForm):
            @classmethod
            def from_sexp(cls, sexp):
                pass  # pragma: no cover


def test_special_form_duplicate_id_raises_value_error():
    class Child2(nodes.SpecialForm):
        id = "child2"

        @classmethod
        def from_sexp(cls, sexp):
            pass  # pragma: no cover

    with pytest.raises(ValueError, match="already defined"):

        @dataclass
        class Child2(nodes.SpecialForm):  # noqa: F811
            id = "child2"

            @classmethod
            def from_sexp(cls, sexp):
                pass  # pragma: no cover


def test_special_form_dc_duplicate_id_raises_value_error():
    @dataclass
    class Child3(nodes.SpecialForm):
        id = "child3"

        @classmethod
        def from_sexp(cls, sexp):
            pass  # pragma: no cover

    with pytest.raises(ValueError, match="already defined"):

        @dataclass
        class Child3(nodes.SpecialForm):  # noqa: F811
            id = "child3"

            @classmethod
            def from_sexp(cls, sexp):
                pass  # pragma: no cover


def test_special_form_dc_with_slots_duplicate_id_raises_value_error():
    @dataclass(slots=True)
    class Child4(nodes.SpecialForm):
        id = "child4"

        @classmethod
        def from_sexp(cls, sexp):
            pass  # pragma: no cover

    with pytest.raises(ValueError, match="already defined"):

        @dataclass(slots=True)
        class Child4(nodes.SpecialForm):  # noqa: F811
            id = "child4"

            @classmethod
            def from_sexp(cls, sexp):
                pass  # pragma: no cover
