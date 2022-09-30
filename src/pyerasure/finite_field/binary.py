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


class Binary:
    """The binary finite field class."""

    """The maximum value of the finite field."""
    max_value: int = 0x01

    @classmethod
    def is_binary(cls) -> bool:
        """Check if the field is binary."""
        return True

    @classmethod
    def elements_to_bytes(cls, elements: int) -> int:
        """Convert the number of elements to the number of bytes."""
        return (elements + 7) // 8

    @classmethod
    def bytes_to_elements(cls, bytes: int) -> int:
        """Convert the number of bytes to the number of elements."""
        return bytes * 8

    @classmethod
    def get_value(cls, elements: bytearray, index: int) -> int:
        """Return the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")
        return (elements[index // 8] >> (index % 8)) & 0x1

    @classmethod
    def set_value(cls, elements: bytearray, index: int, value: int):
        """Set the value of the element at the given index."""
        if index >= cls.bytes_to_elements(len(elements)):
            raise ValueError("index out of range")
        if value < 0 or value > cls.max_value:
            raise ValueError("value must be 0 or 1")
        if value == 0:
            elements[index // 8] &= ~(1 << (index % 8))
        else:
            elements[index // 8] |= 1 << (index % 8)

    @classmethod
    def vector_add_into(cls, x: bytearray, y: bytearray):
        """Add y into x."""
        if len(x) != len(y):
            raise ValueError("x and y must have the same length")
        for i in range(len(x)):
            x[i] ^= y[i]

    @classmethod
    def vector_multiply_add_into(cls, x: bytearray, y: bytes, c: int):
        """
        Multiply the vector y with the constant c and then add the result
        to vector x.
        """
        assert len(x) == len(y)
        assert c <= cls.max_value

        if c == 0:
            return

        if c != 1:
            raise ValueError("c must be 0 or 1")

        for i in range(len(x)):
            x[i] ^= y[i]

    @classmethod
    def vector_multiply_subtract_into(cls, x: bytearray, y: bytes, c: int):
        """Multiply the vector x with the vector y and subtract the result from c."""
        assert c <= cls.max_value
        cls.vector_multiply_add_into(x, y, c)
