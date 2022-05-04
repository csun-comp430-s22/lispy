from collections.abc import Iterable
from itertools import zip_longest

from lispyc.exceptions import CyclicTypeError, UnificationError
from lispyc.nodes import FunctionType, ListType, Type, UnknownType

__all__ = ("Unifier",)


class Unifier:
    """TODO."""

    def __init__(self):
        self._map: dict[UnknownType, Type] = {}

    def unify(self, left: Type, right: Type) -> None:
        """Unify the `left` and `right` types.

        Raise UnificationError if unifying the two types fails.
        """
        left = self.get_set_representative(left)
        right = self.get_set_representative(right)

        if left == right:
            return

        match left, right:
            case UnknownType() as left, _:
                self._add_mapping(left, right)
            case _, UnknownType() as right:
                self._add_mapping(right, left)
            case ListType() as left, ListType() as right:
                self.unify(left.element_type, right.element_type)
            case FunctionType() as left, FunctionType() as right:
                self.unify(left.return_type, right.return_type)
                self._unify_many(left.parameter_types, right.parameter_types)
            case _:
                raise UnificationError(f"Unification failed: mismatched types {left} and {right}")

    def _unify_many(self, left: Iterable[Type], right: Iterable[Type]) -> None:
        """Unify pairs from `left` and `right`."""
        for left_type, right_type in zip_longest(left, right):
            if left_type is None or right_type is None:
                raise UnificationError("Unification failed: unequal number of types")
            else:
                self.unify(left_type, right_type)

    def _add_mapping(self, source: UnknownType, dest: Type) -> None:
        """Map the unknown `source` type to `dest` type if it's not cyclic."""
        if self._has_unknown(dest, source):
            # TODO: Include the cyclic path in the exception message.
            raise CyclicTypeError("Unification failed: attempt to create cyclic type")
        else:
            self._map[source] = dest

    def get_set_representative(self, t: Type) -> Type:
        """Return the set representative type for `t`."""
        # Assume all keys are of UnknownType as denoted by the map's type annotation.
        while next_type := self._map.get(t):  # type: ignore
            t = next_type

        return t

    def get_transitive_set_representative(self, t: Type) -> Type:
        """Return the set representative for `t` with set representatives for its nested types."""
        match t := self.get_set_representative(t):
            case ListType(element):
                return ListType(self.get_transitive_set_representative(element))
            case FunctionType(params, ret):
                return FunctionType(
                    tuple(map(self.get_transitive_set_representative, params)),
                    self.get_transitive_set_representative(ret),
                )
            case _:
                return t

    def _has_unknown(self, t: Type, unknown: UnknownType) -> bool:
        """Return True if `t` is `unknown` or contains it."""
        match t := self.get_set_representative(t):
            case UnknownType():
                return t is unknown
            case ListType(element):
                return element is unknown
            case FunctionType(params, ret):
                # Check if it's the return type or one of the parameters.
                return self._has_unknown(ret, unknown) or any(
                    self._has_unknown(p, unknown) for p in params
                )
            case _:
                return False
