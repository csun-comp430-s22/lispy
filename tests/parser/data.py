from lispyc.nodes import ComposedForm, Constant, List, Variable

__all__ = (
    "FORM_PROGRAMS",
    "FORM_NODES",
    "FORMS",
    "MULTIPLE_FORM_PROGRAMS",
    "MULTIPLE_FORM_NODES",
    "MULTIPLE_FORMS",
)

FORM_PROGRAMS = [
    "()",
    "(a)",
    "(1)",
    "(-7.9)",
    "(true)",
    "99",
    "9.2",
    "false",
    "b2_1",
    "nil",
    "(list 23 false)",
    "(x y 1)",
]

FORM_NODES = [
    List(()),
    ComposedForm(Variable("a"), ()),
    ComposedForm(Constant(1), ()),
    ComposedForm(Constant(-7.9), ()),
    ComposedForm(Constant(True), ()),
    Constant(99),
    Constant(9.2),
    Constant(False),
    Variable("b2_1"),
    Variable("nil"),
    List((Constant(23), Constant(False))),
    ComposedForm(Variable("x"), (Variable("y"), Constant(1))),
]

FORMS = list(zip(FORM_PROGRAMS, FORM_NODES))

MULTIPLE_FORM_PROGRAMS = [
    "1 2",
    "a b c",
    "false (x a b)",
    "(list 1) dx1",
    "a 1 false 6.6",
    "(x a) nil ()",
]

MULTIPLE_FORM_NODES = [
    (Constant(1), Constant(2)),
    (Variable("a"), Variable("b"), Variable("c")),
    (Constant(False), ComposedForm(Variable("x"), (Variable("a"), Variable("b")))),
    (List((Constant(1),)), Variable("dx1")),
    (Variable("a"), Constant(1), Constant(False), Constant(6.6)),
    (ComposedForm(Variable("x"), (Variable("a"),)), Variable("nil"), List(())),
]

MULTIPLE_FORMS = list(zip(MULTIPLE_FORM_PROGRAMS, MULTIPLE_FORM_NODES))
