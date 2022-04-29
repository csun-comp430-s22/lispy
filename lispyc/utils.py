__all__ = ("Abstract",)


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
