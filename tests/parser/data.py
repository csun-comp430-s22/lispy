from lispyc.nodes import ComposedForm, Constant, List, Variable

__all__ = ("FORM_PROGRAMS", "FORM_NODES", "FORMS")

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
