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

from . import FullTable
from . import Binary


class Binary4:
    """The binary4 finite field class."""

    """The maximum value of the finite field."""
    max_value: int = 0x0F

    def __init__(self, prime: int = 19):
        """The binary4 finite field constructor."""
        self._prime = prime
        self._table = FullTable(self._prime)
        assert self._table.degree == 4

    @classmethod
    def is_binary(cls) -> bool:
        """Check if the field is binary."""
        return False

    @classmethod
    def elements_to_bytes(cls, elements: int) -> int:
        """Convert the number of elements to the number of bytes."""
        return elements // 2 + elements % 2

    @classmethod
    def bytes_to_elements(cls, bytes: int) -> int:
        """Convert the number of bytes to the number of elements."""
        return bytes * 2

    @classmethod
    def get_value(cls, elements: bytearray, index: int) -> int:
        """Return the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")

        array_index = index // 2
        if index % 2 == 1:
            # Get upper nibble
            return (elements[array_index] & 0xF0) >> 4
        else:
            # Get lower nibble
            return elements[array_index] & 0x0F

    @classmethod
    def set_value(cls, elements: bytearray, index: int, value: int):
        """Set the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")
        if value < 0 or value > cls.max_value:
            raise ValueError("value must be between 0 and 15")

        array_index = index // 2
        if index % 2 == 1:
            # write upper nibble
            elements[array_index] &= 0x0F
            elements[array_index] |= value << 4
        else:
            # write lower nibble
            elements[array_index] &= 0xF0
            elements[array_index] |= value

    @classmethod
    def add(cls, lhs: int, rhs: int) -> int:
        """Add two elements."""
        if lhs < 0 or lhs > cls.max_value:
            raise ValueError("lhs must be between 0 and 15")
        return lhs ^ rhs

    def invert(self, x: int) -> int:
        """Invert the given element."""
        return self._table.divide(1, x)

    @classmethod
    def vector_add_into(cls, x: bytearray, y: bytearray):
        """Add y into x."""
        # Use the binary add function
        Binary.vector_add_into(x, y)

    def vector_multiply_add_into(self, x: bytearray, y: bytes, c: int):
        """
        Multiply the vector y with the constant c and then add the result
        to vector x.
        """

        assert len(x) == len(y)
        assert c <= self.max_value

        for i in range(len(x)):
            x1 = x[i] >> 4
            x1 ^= self._table.multiply(y[i] >> 4, c)
            x2 = x[i] & 0xF
            x2 ^= self._table.multiply(y[i] & 0xF, c)
            x[i] = (x1 << 4) | x2

    def vector_multiply_subtract_into(self, x: bytearray, y: bytes, c: int):
        """Multiply the vector x with the vector y and subtract the result from c."""
        self.vector_multiply_add_into(x, y, c)

    def vector_multiply_into(self, x: bytearray, c: int):
        """Multiply the vector x with the vector y."""

        assert c <= self.max_value
        for i in range(len(x)):
            x1 = x[i] >> 4
            x1 = self._table.multiply(x1, c)
            x2 = x[i] & 0xF
            x2 = self._table.multiply(x2, c)
            x[i] = (x1 << 4) | x2
