__all__ = ("Abstract", "MatchExclusionsMeta")


class Abstract:
    """Prevent instantiation of subclasses flagged as abstract.

    Direct subclasses are implicitly flagged as abstract. However, indirect children are implicitly
    marked as concrete (non-abstract). The flag can be explicitly controlled by passing the
    `abstract` kwarg when defining the class, as shown in the examples below.

    >>> class Base1(Abstract): ...
    >>> class Base2(Base1, abstract=True): ...
    >>> class Concrete1(Base1): ...
    >>> class Concrete2(Base2): ...
    >>>
    >>> Base1()  # TypeError
    >>> Base2()  # TypeError
    >>> Concrete1()  # Okay!
    >>> Concrete2()  # Okay!
    """

    __abstract = True

    def __new__(cls, *args, **kwargs):
        """Create a new instance of `cls`. Raise a TypeError if `cls` is flagged as abstract."""
        if cls.__abstract:
            raise TypeError(f"Cannot instantiate abstract class {cls.__name__!r}.")

        return super().__new__(cls)

    def __init_subclass__(cls, abstract: bool | None = None, **kwargs):
        super().__init_subclass__(**kwargs)

        if abstract is not None:
            # Set to the explicitly given value.
            cls.__abstract = abstract
        elif Abstract in cls.__bases__:
            # Implicitly True only for direct children of Abstract.
            cls.__abstract = True
        else:
            cls.__abstract = False


class MatchExclusionsMeta(type):
    """Exclude arguments from `__match_args__`.

    Exclusions can be specified by passing an iterable as the `exclude` keyword argument:

    >>> @dataclasses.dataclass
    >>> class Class(metaclass=MatchExclusionsMeta, exclude={"arg1"}):
    >>>    arg1: int
    >>>    arg2: int
    >>>
    >>> Class.__match_args__
    >>> ("arg2",)

    Subclasses inherit the exclusions, and can override them by explicitly specifying the kwarg.
    """

    def __new__(mcs, name, bases, ns, exclude=None, **kwargs):  # noqa: ANN001
        """Create a new instance of `mcs` and store the given exclusions."""
        cls = super().__new__(mcs, name, bases, ns, **kwargs)

        # Only store it if it's explicitly set, which overrides the parent's value.
        # Otherwise, it remains the same and can inherit the value from the parent.
        if exclude is not None:
            cls.__match_args_exclusions = frozenset(exclude)

        return cls

    def __getattribute__(cls, name: str):
        value = super().__getattribute__(name)
        if name == "__match_args__":
            try:
                value = tuple(arg for arg in value if arg not in cls.__match_args_exclusions)
            except AttributeError:
                pass  # No exclusions were set, but that's okay.

        return value
