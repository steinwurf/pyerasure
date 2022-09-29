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

    @staticmethod
    def elements_to_bytes(elements: int) -> int:
        """Convert the number of elements to the number of bytes."""
        return (elements + 7) // 8

    @staticmethod
    def get_value(elements: bytearray, index: int) -> int:
        """Return the value of the element at the given index."""
        if index >= len(elements):
            raise ValueError("index out of range")
        return (elements[index // 8] >> (index % 8)) & 0x1

    @staticmethod
    def set_value(elements: bytearray, index: int, value: int):
        """Set the value of the element at the given index."""
        if index >= len(elements):
            raise ValueError("index out of range")
        if value != 0 and value != 1:
            raise ValueError("value must be 0 or 1")
        if value == 0:
            elements[index // 8] &= ~(1 << (index % 8))
        else:
            elements[index // 8] |= 1 << (index % 8)

    def vector_multiply_add_into(self, x: bytearray, y: bytes, c: int):
        """Multiply the vector x with the vector y and add the result to c."""
        if c == 0:
            return

        if c != 1:
            raise ValueError("c must be 0 or 1")

        for i in range(len(x)):
            x[i] ^= y[i] & c
