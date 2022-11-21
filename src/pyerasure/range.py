# License for Commercial Usage
# Distributed under the "PYERASURE EVALUATION LICENSE 1.3"
# Licensees holding a valid commercial license may use this project in
# accordance with the standard license agreement terms provided with the
# Software (see accompanying file LICENSE.rst or
# https://www.steinwurf.com/license), unless otherwise different terms and
# conditions are agreed in writing between Licensee and Steinwurf ApS in which
# case the license will be regulated by that separate written agreement.
#
# License for Non-Commercial Usage
# Distributed under the "PYERASURE RESEARCH LICENSE 1.2"
# Licensees holding a valid research license may use this project in accordance
# with the license agreement terms provided with the Software
# See accompanying file LICENSE.rst or https://www.steinwurf.com/license

from __future__ import annotations

from typing import Union


class Range:

    """
    A range.
    We follow Dijkstra's advice and start numbering from zero:
    http://www.cs.utexas.edu/users/EWD/ewd08xx/EWD831.PDF
    """

    def __init__(
        self,
        lower_bound: int,
        upper_bound: int,
    ):
        """
        The range constructor.

        :param lower_bound: The lower bound of the range.
        :param upper_bound: The upper bound of the range.
        """

        if lower_bound > upper_bound:
            raise ValueError(
                "The upper bound must be greater than or equal the lower bound. "
                f"Got lower_bound={lower_bound} and upper_bound={upper_bound}."
            )

        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    @property
    def lower_bound(self) -> int:
        """The lower bound of the range."""
        return self._lower_bound

    @property
    def upper_bound(self) -> int:
        """The upper bound of the range."""
        return self._upper_bound

    def pop(self) -> int:
        """Pop the first element in the range."""
        self._lower_bound += 1
        return self._lower_bound - 1

    def push(self) -> int:
        """Push an element to the upper bound of the range."""
        self._upper_bound += 1
        return self._upper_bound

    def slide(self, amount: int):
        """Slide the range by a given amount."""
        self._lower_bound += amount
        self._upper_bound += amount

    def empty(self) -> bool:
        """Check if the range is empty."""
        return self.lower_bound == self.upper_bound

    def intersect(self, other: Range) -> Range:
        """Compute the intersection of two ranges."""
        return Range(
            max(self.lower_bound, other.lower_bound),
            min(self.upper_bound, other.upper_bound),
        )

    def intersects(self, other: Range) -> bool:
        """Check if the range intersects with another range."""
        return not self.intersect(other).empty()

    def __len__(self) -> int:
        return self.upper_bound - self.lower_bound

    def __eq__(self, other: object) -> bool:
        """Check if the range is equal to another range."""
        if not isinstance(other, Range):
            return False
        return (
            self.lower_bound == other.lower_bound
            and self.upper_bound == other.upper_bound
        )

    def __contains__(self, item: Union[int, Range]) -> bool:
        """Check if the item is in the range."""
        if isinstance(item, Range):
            return (
                self.lower_bound <= item.lower_bound
                and item.upper_bound <= self.upper_bound
            )
        else:
            return self.lower_bound <= item < self.upper_bound

    def __iter__(self):
        return iter(range(self.lower_bound, self.upper_bound))

    def __repr__(self) -> str:
        return f"Range({self.lower_bound}, {self.upper_bound})"
