from collections.abc import Iterable
from itertools import zip_longest

from lispyc.nodes import types

from .types import UnknownType

__all__ = ("Unifier",)


class Unifier:
    """Unification of types."""

    def __init__(self):
        self._map: dict[UnknownType, types.Type] = {}

    def unify(self, left: types.Type, right: types.Type) -> None:
        """Unify the `left` and `right` types."""
        left = self._get_set_representative(left)
        right = self._get_set_representative(right)

        if left == right:
            return

        match left, right:
            case UnknownType() as left, _:
                self._add_mapping(left, right)
            case _, UnknownType() as right:
                self._add_mapping(right, left)
            case types.ListType() as left, types.ListType() as right:
                self.unify(left.element_type, right.element_type)
            case types.FunctionType() as left, types.FunctionType() as right:
                self.unify(left.return_type, right.return_type)
                self._unify_many(left.parameter_types, right.parameter_types)
            case _:
                raise ValueError("Unification failed: mismatched types.")

    def _unify_many(self, left: Iterable[types.Type], right: Iterable[types.Type]) -> None:
        """Unify pairs from `left` and `right`."""
        for left_type, right_type in zip_longest(left, right):
            if left_type is None or right_type is None:
                raise ValueError("Unification failed: unequal number of types.")
            else:
                self.unify(left_type, right_type)

    def _add_mapping(self, source: UnknownType, dest: types.Type) -> None:
        """Map the unknown `source` type to `dest` type if it's not cyclic."""
        if self._has_unknown(dest, source):
            raise ValueError("Unification failed: attempt to create cyclic type")
        else:
            self._map[source] = dest

    def _get_set_representative(self, t: types.Type) -> types.Type:
        """Return the set representative type for `t`."""
        # Assume all keys are of UnknownType as denoted by the map's type annotation.
        while next_type := self._map.get(t):  # type: ignore
            t = next_type

        return t

    def _get_transitive_set_representative(self, t: types.Type) -> types.Type:
        """Return the set representative for `t` with set representatives for its nested types."""
        match t := self._get_set_representative(t):
            case types.ListType(element):
                return types.ListType(self._get_transitive_set_representative(element))
            case types.FunctionType(params, ret):
                return types.FunctionType(
                    tuple(map(self._get_transitive_set_representative, params)),
                    self._get_transitive_set_representative(ret),
                )
            case _:
                return t

    def _has_unknown(self, t: types.Type, unknown: UnknownType) -> bool:
        """Return True if `t` is `unknown` or contains it."""
        match t := self._get_set_representative(t):
            case UnknownType():
                return t is unknown
            case types.ListType(element):
                return element is unknown
            case types.FunctionType(params, ret):
                # Check if it's the return type or one of the parameters.
                return self._has_unknown(ret, unknown) or any(
                    self._has_unknown(p, unknown) for p in params
                )
            case _:
                return False
