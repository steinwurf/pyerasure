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

from . import Binary, Binary4, Binary8


class Element:
    def __init__(self, field: Union[Binary, Binary4, Binary8], value: int):
        """
        The vector constructor.

        :param field: The field to use.
        :param value: The value.
        """
        self.field = field
        self.value = value

    def __repr__(self) -> str:
        return f"Element<{self.field}>, {self.value})"

    def __add__(self, other: Element) -> Element:
        self.field.add(self.value, other.value)
        return self

    def __sub__(self, other: Element) -> Element:
        return self.__add__(other)

    def __invert__(self) -> Element:
        self.field.invert(self.value)
        return self

    def __eq__(self, other: Union[Element, int]) -> bool:
        if isinstance(other, Element):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Union[Element, int]) -> bool:
        return not self.__eq__(other)
