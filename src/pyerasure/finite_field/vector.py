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

from typing import Union, Tuple

from . import Binary, Binary4, Binary8, Element
from ..range import Range


class Vector:
    """A Vector of elements."""

    class Iterator:
        def __init__(self, vector: Vector):
            self.vector = vector
            self.index = vector.offset

        def __next__(self) -> Tuple[int, Element]:
            if self.index >= self.vector.upper_bound:
                raise StopIteration
            value = self.vector[self.index]
            index = self.index
            self.index += 1
            return index, value

    @staticmethod
    def allocate(
        field: Union[Binary, Binary4, Binary8],
        elements: int,
        offset: int = 0,
    ) -> Vector:
        return Vector(
            field, bytearray(field.elements_to_bytes(elements)), elements, offset
        )

    def __init__(
        self,
        field: Union[Binary, Binary4, Binary8],
        data: bytearray,
        elements: int = None,
        offset: int = 0,
    ):
        """
        The vector constructor.

        :param field: The field to use.
        :param data: The data to use.
        :param offset: The offset of the data.
        """

        if offset < 0:
            raise ValueError("Offset must be positive")

        if elements is None:
            elements = field.bytes_to_elements(len(data))

        if elements < 0:
            raise ValueError("Elements must be positive")

        if field.elements_to_bytes(elements) > len(data):
            raise ValueError("Data is too small")

        self.field = field
        self.data = data
        self.offset = offset
        self.elements = elements

    @property
    def lower_bound(self) -> int:
        return self.offset

    @property
    def upper_bound(self) -> int:
        return self.offset + self.elements

    @property
    def range(self) -> Range:
        return Range(self.lower_bound, self.upper_bound)

    def copy(self) -> Vector:
        return Vector(self.field, self.data.copy(), self.elements, self.offset)

    def __repr__(self) -> str:
        return f"Vector<{self.field}>, {self.data}, {self.offset}, {self.elements}"

    def __iadd__(self, other: Vector) -> Vector:
        self.field.vector_add_into(memoryview(self.data)[: len(other.data)], other.data)
        if len(self.data) < len(other.data):
            self.data.extend(memoryview(other.data)[len(other.data) :])
        return self

    def __add__(self, other: Vector) -> Vector:
        result = self.copy()
        result += other
        return result

    def __sub__(self, other: Vector) -> Vector:
        return self.__add__(other)

    def __isub__(self, other: Vector) -> Vector:
        return self.__iadd__(other)

    def __mul__(self, other: Union[int, Element]) -> Vector:
        result = self.copy()
        result *= other
        return result

    def __imul__(self, other: Union[int, Element]) -> Vector:
        if isinstance(other, Element):
            other = other.value
        self.field.vector_multiply_into(self.data, other)
        return self

    def __len__(self) -> int:
        return self.elements

    def __getitem__(self, index: int) -> Element:
        if index < self.offset or index >= self.upper_bound:
            raise IndexError("Index out of range")
        return Element(self.field, self.field.get_value(self.data, index))

    def __setitem__(self, index: int, value: Union[int, Element]) -> None:

        if index < self.offset or index >= self.upper_bound:
            raise IndexError("Index out of range")

        if isinstance(value, Element):
            value = value.value

        self.field.set_value(self.data, index, value)

    def __iter__(self) -> Vector.Iterator:

        return Vector.Iterator(self)

    def __str__(self) -> str:
        # print elements horizontally
        result = []
        for _, element in self:
            if element.value == 0:
                result.append("__")
            else:
                result.append(f"{element.value :02x}")
        return " ".join(result)
