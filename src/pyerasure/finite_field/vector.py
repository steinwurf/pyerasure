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
        """Iterator for the vector."""

        def __init__(self, vector: Vector):
            self.vector = vector
            self.index = vector.offset

        def __next__(self) -> Tuple[int, Element]:
            """Return the next index and element in the vector."""
            if self.index >= self.vector.upper_bound:
                raise StopIteration
            value = self.vector[self.index]
            index = self.index
            self.index += 1
            return index, value

    @staticmethod
    def allocateBytes(
        field: Union[Binary, Binary4, Binary8], bytes: int, offset: int = 0
    ) -> Vector:
        """
        Allocate a vector of elements.

        :param field: The field to use.
        :param bytes: The number of bytes to allocate.
        :param offset: The offset of the data in elements.
        :return: The allocated vector.
        """
        return Vector(field, bytearray(bytes), field.bytes_to_elements(bytes), offset)

    @staticmethod
    def allocateCoefficients(
        field: Union[Binary, Binary4, Binary8],
        elements: int,
        offset: int = 0,
    ) -> Vector:
        """
        Allocate a vector of coefficients.

        :param field: The field to use.
        :param elements: The number of elements to allocate.
        :param offset: The offset in elements.
        :return: The allocated vector.
        """
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
        :param elements: The number of elements in the vector.
        :param offset: The offset of the data in elements.
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
        """The lower bound of the vector in elements."""
        return self.offset

    @property
    def upper_bound(self) -> int:
        """The upper bound of the vector in elements."""
        return self.offset + self.elements

    @property
    def range(self) -> Range:
        """The range of the vector."""
        return Range(self.lower_bound, self.upper_bound)

    @property
    def bytes(self) -> int:
        """
        Return the number of bytes in the vector.
        """
        return len(self.data)

    def __len__(self) -> int:
        """
        Return the number of elements in the vector.
        """
        return self.elements

    def copy(self) -> Vector:
        """
        Copy the vector.

        :return: The copied vector.
        """
        return Vector(self.field, self.data.copy(), self.elements, self.offset)

    def add(self, other: Vector) -> Vector:
        """
        Add another vector to this vector.

        :param other: The other vector.
        :return: The result of the addition.
        """
        return self.__iadd__(other)

    def multiply(self, element: Union[int, Element]) -> Vector:
        """
        Add an element to this vector.

        :param element: The element.
        :return: The result of the multiplication.
        """
        return self.__iadd__(element)

    def multiply_add(self, other: Vector, element: Union[int, Element]) -> Vector:
        """
        Multiply another vector with an element and add the result to this vector.

        :param other: The other vector.
        :param element: The element.
        :return: The result of the multiplication and addition.
        """

        if isinstance(element, Element):
            element = element.value

        self.field.vector_multiply_add_into(
            memoryview(self.data)[: len(other.data)], other.data, element
        )

        if len(self.data) < len(other.data):
            extra = Vector(
                self.field,
                other[len(self.data) :],
                other.elements - self.elements,
                other.offset + self.elements,
            )
            extra *= element
            self += extra
        return self

    def __iadd__(self, other: Vector) -> Vector:
        """
        Add another vector to this vector.
        """

        if self.field != other.field:
            raise ValueError("Fields must be the same")

        if not self.range.intersects(other.range):
            raise ValueError(f"Ranges must intersect {self.range} {other.range}")

        lowerSymbolDiff = self.lower_bound - other.lower_bound
        lowerByteDiff = self.field.elements_to_bytes(lowerSymbolDiff)
        if lowerByteDiff == 0:
            # The vectors are aligned
            # this  |------...
            # other |------...
            self.field.vector_add_into(
                memoryview(self.data)[: len(other.data)],
                memoryview(other.data)[: len(self.data)],
            )
        elif lowerByteDiff < 0:
            # The other vector is further ahead
            # this  |------...
            # other   |----...
            self.field.vector_add_into(
                memoryview(self.data)[
                    -lowerByteDiff : -lowerByteDiff + len(other.data)
                ],
                memoryview(other.data)[: len(self.data) + lowerByteDiff],
            )
        else:
            # The other vector is further behind
            # this    |----...
            # other |------...
            self.offset = other.offset
            self.elements = max(self.elements, other.elements)
            self.data = bytearray(lowerByteDiff) + self.data
            self.field.vector_add_into(
                memoryview(self.data)[: len(other.data)],
                memoryview(other.data)[: len(self.data)],
            )
            # raise ValueError("The other vector is further behind")

        # Handle the extra elements
        upperSymbolDiff = other.upper_bound - self.upper_bound
        upperByteDiff = self.field.elements_to_bytes(upperSymbolDiff)
        if upperByteDiff > 0:
            # The other vector is longer
            # this  ...-----|
            # other ...---------|

            # this  |-----|
            # other |---------|
            # extra       |---|
            # lowerDiff = 0
            # upperDiff = 4
            # other[len(this) + lowerDiff:]

            # this  |-----|
            # other    |-----|
            # extra       |--|
            # lowerDiff = -4
            # upperDiff = 3
            # other[len(this) + lowerDiff:]

            # this   |-----|
            # other |---------|
            # extra        |--|
            # lowerDiff = 1
            # upperDiff = 3
            # other[len(this) + lowerDiff:]

            extra = Vector(
                self.field,
                memoryview(other.data)[len(self.data) + lowerByteDiff :],
                len(other.range.intersect(self.range)),
                other.offset + self.elements,
            )
            self += extra
        else:
            # The vectors are the same length
            # this  ...-----|
            # other ...-----|
            # or
            # The other vector is shorter
            # this  ...---------|
            # other ...-----|
            pass

        self.offset = min(self.offset, other.offset)

        return self

    def __add__(self, other: Vector) -> Vector:
        """
        Add this vector and another vector and return the result as a new vector.
        """
        result = self.copy()
        result += other
        return result

    def __sub__(self, other: Vector) -> Vector:
        """
        Substract this vector and another vector and return the result as a new vector.
        """
        return self.__add__(other)

    def __isub__(self, other: Vector) -> Vector:
        """
        Substract another vector from this vector.
        """
        return self.__iadd__(other)

    def __mul__(self, other: Union[int, Element]) -> Vector:
        """
        Multiply this vector with an element and return the result as a new vector.
        """
        result = self.copy()
        result *= other
        return result

    def __imul__(self, element: Union[int, Element]) -> Vector:
        """
        Multiply this vector with an element.
        """
        if isinstance(element, Element):
            element = element.value
        self.field.vector_multiply_into(self.data, element)
        return self

    def __getitem__(self, index: int) -> Element:
        """
        Get an element from the vector.

        :param index: The index of the element.
        :return: The element.
        """
        if index < self.offset or index >= self.upper_bound:
            raise IndexError("Index out of range")
        return Element(self.field, self.field.get_value(self.data, index - self.offset))

    def __setitem__(self, index: int, element: Union[int, Element]) -> None:
        """
        Set an element in the vector.

        :param index: The index of the element.
        :param element: The the element.
        """
        if index < self.offset or index >= self.upper_bound:
            raise IndexError("Index out of range")

        if isinstance(element, Element):
            element = element.value

        self.field.set_value(self.data, index - self.offset, element)

    def __eq__(self, other: Vector) -> bool:
        """
        Check if this vector is equal to another vector.

        :param other: The other vector.
        :return: True if the vectors are equal, False otherwise.
        """
        if self.field != other.field:
            return False

        if self.range != other.range:
            return False

        return self.data == other.data

    def __ne__(self, other: Vector) -> bool:
        """
        Check if this vector is not equal to another vector.

        :param other: The other vector.
        :return: True if the vectors are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def __iter__(self) -> Vector.Iterator:
        """
        Return an iterator for the vector.
        """
        return Vector.Iterator(self)

    def __str__(self) -> str:
        """
        Return a string representation of the vector.
        0 values are represented by a dot.
        :return: The string representation.
        """
        result = []
        for _, element in self:
            if element.value == 0:
                result.append(" .")
            else:
                result.append(f"{element.value :02x}")
        return " ".join(result)

    def __repr__(self) -> str:
        return f"Vector<{self.field}>, {self.data}, {self.offset}, {self.elements}"
