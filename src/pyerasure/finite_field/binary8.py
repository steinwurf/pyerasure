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

from typing import Final

from . import FullTable
from . import Binary


class Binary8:
    """The binary8 finite field class."""

    """The maximum value of the finite field."""
    max_value: Final[int] = 0xFF

    """The number of elements per byte."""
    elements_per_byte: Final[int] = 1

    """The number of bits per element."""
    bits_per_element: Final[int] = 8

    def __init__(self, prime: int = 285):
        """The binary8 finite field constructor."""
        self._prime = prime
        self._table = FullTable(self._prime)
        assert self._table.degree == 8

    @classmethod
    def is_binary(cls) -> bool:
        """Check if the field is binary."""
        return False

    @classmethod
    def elements_to_bytes(cls, elements: int) -> int:
        """Convert the number of elements to the number of bytes."""
        return elements

    @classmethod
    def bytes_to_elements(cls, bytes: int) -> int:
        """Convert the number of bytes to the number of elements."""
        return bytes

    @classmethod
    def get_value(cls, elements: bytes, index: int) -> int:
        """Return the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")
        return elements[index]

    @classmethod
    def set_value(cls, elements: bytearray, index: int, value: int):
        """Set the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")
        if value < 0 or value > cls.max_value:
            raise ValueError("value must be between 0 and 255")
        elements[index] = value

    @classmethod
    def add(cls, lhs: int, rhs: int) -> int:
        """Add two elements."""
        if lhs < 0 or lhs > cls.max_value:
            raise ValueError("lhs must be between 0 and 255")
        return lhs ^ rhs

    def invert(self, x: int) -> int:
        """Invert the given element."""
        return self._table.divide(1, x)

    @classmethod
    def vector_add_into(cls, x: bytearray, y: bytes):
        """Add y into x."""
        # Use the binary add function
        Binary.vector_add_into(x, y)

    @classmethod
    def vector_subtract_into(cls, x: bytearray, y: bytes):
        """Substract y into x."""
        cls.vector_add_into(x, y)

    def vector_multiply_add_into(self, x: bytearray, y: bytes, c: int):
        """
        Multiply the vector y with the constant c and then add the result
        to vector x.
        """
        assert x is not None
        assert y is not None

        if len(x) > len(y):
            raise ValueError("x must be at least as long as y")

        if c > self.max_value:
            raise ValueError(f"c must be less than {self.max_value}")

        for i in range(len(y)):
            x[i] ^= self._table.multiply(y[i], c)

    def vector_multiply_into(self, x: bytearray, c: int):
        """Multiply the vector x with the constant c."""

        if c == 0:
            for i in range(len(x)):
                x[i] = 0
            return

        if c == 1:
            return

        if c > self.max_value:
            raise ValueError(f"c must be less than {self.max_value}")

        for i in range(len(x)):
            x[i] = self._table.multiply(x[i], c)

    def vector_multiply_subtract_into(self, x: bytearray, y: bytes, c: int):
        """Multiply the vector y with the constant c and subtract the result from x."""
        assert x is not None
        assert y is not None
        self.vector_multiply_add_into(x, y, c)
