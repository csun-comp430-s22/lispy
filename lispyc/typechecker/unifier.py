from collections.abc import Iterable

from . import types


class Unifier:
    """Unification of types."""

    def __init__(self):
        self._map: dict[types.UnknownType, types.Type] = {}

    def unify(self, left: types.Type, right: types.Type) -> None:
        """Unify the `left` and `right` types."""
        left = self._get_set_representative(left)
        right = self._get_set_representative(right)

        if left is right:
            return

        match left, right:
            case types.UnknownType(), _:
                self._add_mapping(left, right)
            case _, types.UnknownType():
                self._add_mapping(right, left)
            case types.ListType(), types.ListType():
                self.unify(left.element_type, right.element_type)
            case types.FunctionType(), types.FunctionType():
                self.unify(left.return_type, right.return_type)
                self._unify_many(left.parameter_types, right.parameter_types)
            case _:
                raise ValueError("Unification failed: mismatched types.")

    def _unify_many(self, left: Iterable[types.Type], right: Iterable[types.Type]) -> None:
        """Unify pairs from `left` and `right`."""
        left_iter = iter(left)
        right_iter = iter(right)

        for left_type, right_type in zip(left_iter, right_iter):
            self.unify(left_type, right_type)

        if next(left_iter, None) or next(right_iter, None):
            raise ValueError("Unification failed: unequal number of types.")

    def _add_mapping(self, source: types.UnknownType, dest: types.Type) -> None:
        """Map the unknown `source` type to `dest` type if it's not cyclic."""
        if self._has_unknown(dest, source):
            raise ValueError("Unification failed: attempt to create cyclic type")
        else:
            self._map[source] = dest

    def _get_set_representative(self, t: types.Type) -> types.Type:
        """Return the set representative type for `t`."""
        # Assume all keys are of UnknownType as denoted by the map's type annotation.
        while next_type := self._map.get(t):
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

    def _has_unknown(self, t: types.Type, unknown: types.UnknownType) -> bool:
        """Return True if `t` is `unknown` or contains it."""
        match t := self._get_set_representative(t):
            case types.UnknownType():
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
