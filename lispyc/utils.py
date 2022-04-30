from __future__ import annotations

import typing

__all__ = ("Abstract", "HashableSequence")


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


T = typing.TypeVar("T", covariant=True)


@typing.runtime_checkable
class HashableSequence(typing.Protocol[T]):  # pragma: no cover
    """A sequence which is also hashable."""

    def __hash__(self) -> int:
        ...

    def __reversed__(self) -> typing.Iterator[T]:
        ...

    def __contains__(self, item: object, /) -> bool:
        ...

    def __iter__(self) -> typing.Iterator[T]:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, i: typing.SupportsIndex, /) -> T:
        ...

    def index(  # noqa: D102
        self,
        value: typing.Any,
        start: typing.SupportsIndex = ...,
        stop: typing.SupportsIndex = ...,
        /,
    ) -> int:
        ...

    def count(self, value: typing.Any, /) -> int:  # noqa: D102
        ...
