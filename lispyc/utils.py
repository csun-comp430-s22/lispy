from __future__ import annotations

import inspect
import typing

__all__ = ("Abstract", "is_redefined_dataclass_with_slots")


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

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any):
        """Create a new instance of `cls`. Raise a TypeError if `cls` is flagged as abstract."""
        if cls.__abstract:
            raise TypeError(f"Cannot instantiate abstract class {cls.__name__!r}.")

        return super().__new__(cls)

    def __init_subclass__(cls, /, *, abstract: bool | None = None, **kwargs: typing.Any):
        super().__init_subclass__(**kwargs)

        if abstract is not None:
            # Set to the explicitly given value.
            cls.__abstract = abstract
        elif Abstract in cls.__bases__:
            # Implicitly True only for direct children of Abstract.
            cls.__abstract = True
        else:
            cls.__abstract = False


def is_redefined_dataclass_with_slots(old: type, new: type) -> bool:
    """Return True if `new` is the `old` dataclass redefined with `__slots__."""
    # Must both be dataclasses.
    if "__dataclass_fields__" not in old.__dict__ or "__dataclass_fields__" not in new.__dict__:
        return False

    # Old class must not have __slots__.
    # New class must have __slots__ since that would be the purpose for recreating the class.
    # __slots__ must be checked directly on the class, ignoring any inherited __slots__.
    if "__slots__" in old.__dict__ or "__slots__" not in new.__dict__:
        return False

    # This doesn't definitively indicate it's the same class, but it's good enough.
    return (
        inspect.getmodule(old) == inspect.getmodule(new)
        and old.__name__ == new.__name__
        and old.__bases__ == new.__bases__
    )
