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


class Binary:
    """The binary finite field class."""

    """The maximum value of the finite field."""
    max_value: Final[int] = 0x01

    """The number of elements per byte."""
    elements_per_byte: Final[int] = 8

    """The number of bits per element."""
    bits_per_element: Final[int] = 1

    @classmethod
    def is_binary(cls) -> bool:
        """Check if the field is binary."""
        return True

    @classmethod
    def elements_to_bytes(cls, elements: int) -> int:
        """Convert the number of elements to the number of bytes."""
        return (elements + (Binary.elements_per_byte - 1)) // Binary.elements_per_byte

    @classmethod
    def bytes_to_elements(cls, bytes: int) -> int:
        """Convert the number of bytes to the number of elements."""
        return bytes * Binary.elements_per_byte

    @classmethod
    def get_value(cls, elements: bytes, index: int) -> int:
        """Return the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")
        return (
            elements[index // Binary.elements_per_byte]
            >> (index % Binary.elements_per_byte)
        ) & 0x1

    @classmethod
    def set_value(cls, elements: bytearray, index: int, value: int):
        """Set the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")
        if value < 0 or value > cls.max_value:
            raise ValueError("value must be 0 or 1")
        if value == 0:
            elements[index // Binary.elements_per_byte] &= ~(
                1 << (index % Binary.elements_per_byte)
            )
        else:
            elements[index // Binary.elements_per_byte] |= 1 << (
                index % Binary.elements_per_byte
            )

    @classmethod
    def add(cls, lhs: int, rhs: int) -> int:
        """Add two elements."""
        if lhs < 0 or lhs > cls.max_value:
            raise ValueError("lhs must be 0 and 1")
        return lhs ^ rhs

    @classmethod
    def divide(cls, lhs: int, rhs: int) -> int:
        """Divide two elements."""
        if lhs < 0 or lhs > cls.max_value:
            raise ValueError("lhs must be 0 or 1")
        if rhs < 0 or rhs > cls.max_value:
            raise ValueError("rhs must be 0 or 1")
        return lhs

    @classmethod
    def vector_add_into(cls, x: bytearray, y: bytes):
        """Add y into x."""
        min_len = min(len(x), len(y))
        for i in range(min_len):
            x[i] ^= y[i]

    @classmethod
    def vector_multiply_add_into(cls, x: bytearray, y: bytes, c: int):
        """
        Multiply the vector y with the constant c and then add the result
        to vector x.
        """
        assert x is not None
        assert y is not None

        if c > cls.max_value:
            raise ValueError(f"c must be less than {cls.max_value}")

        if c == 0:
            return

        min_len = min(len(x), len(y))
        for i in range(min_len):
            x[i] ^= y[i]

    @classmethod
    def vector_multiply_into(cls, x: bytearray, c: int):
        """Multiply the vector x with the constant c."""

        if c > cls.max_value:
            raise ValueError(f"c must be less than {cls.max_value}")

        if c == 1:
            return

        for i in range(len(x)):
            x[i] = 0

    @classmethod
    def vector_subtract_into(cls, x: bytearray, y: bytes):
        """Substract y into x."""
        cls.vector_add_into(x, y)

    @classmethod
    def vector_multiply_subtract_into(cls, x: bytearray, y: bytes, c: int):
        """Multiply the vector y with the constant c and subtract the result from x."""
        assert x is not None
        assert y is not None
        cls.vector_multiply_add_into(x, y, c)
