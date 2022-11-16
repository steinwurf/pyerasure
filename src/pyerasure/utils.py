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

from typing import Union
from .finite_field import Binary, Binary4, Binary8

from .range import Range


def floor(a, b) -> int:
    """Return the floor of a/b."""
    return a // b


def ceil(a, b) -> int:
    """Return the ceiling of a/b."""
    return -(-a // b)


def to_frame(elements_per_byte: int, range: Range):
    """
    Convert a range to a frame.
    A frame, in this context, is the set of indecies covered by the range in
    sub-byte fields. For example, if the range is [1, 3] and the elements per
    byte is 2, then the frame is [0, 4].

    :param elements_per_byte: The number of elements per byte.
    :param symbol_range: The range to convert.
    :return: The frame.
    """
    if range.empty():
        # If the range is empty, we return the same empty range.
        return range

    return Range(
        floor(range.lower_bound, elements_per_byte) * elements_per_byte,
        ceil(range.upper_bound, elements_per_byte) * elements_per_byte,
    )


def coefficients_bytes(elements_per_byte: int, window: Range) -> int:
    """
    The number of bytes needed to store the coefficients in the given window.

    :param window: The window.
    """

    frame = to_frame(elements_per_byte, window)
    byte_range = Range(
        (frame.lower_bound) // elements_per_byte,
        (frame.upper_bound) // elements_per_byte,
    )
    return len(byte_range)


def is_coefficients_decoded(
    field: Union[Binary, Binary4, Binary8],
    window: Range,
    coefficients: bytes,
    index: int,
) -> bool:
    """Check if the coefficients are decoded.
    :param field: The finite field.
    :param window: The window.
    :param coefficients: The coefficients.
    :param index: The index of the symbol.
    :return: True if the coefficients are decoded, False otherwise.
    """
    frame = to_frame(field.elements_per_byte, window)
    for i in frame:
        if i not in window or i == index:
            continue

        if field.get_value(coefficients, relative_index(frame, index)) != 0:
            return False

    return True


def relative_index(range: Range, index: int) -> int:
    """Return the relative index of the given index.

    :param range: The range.
    :param index: The index.
    :return: The relative index.
    """
    if index not in range:
        raise ValueError("The index is not in the range.")
    return index - range.lower_bound


def print_coefficients(field: Union[Binary, Binary4, Binary8], coefficients: bytearray):
    """Print the coefficients of a polynomial.

    :param coefficients: The coefficients of the polynomial.
    :param field: The finite field.
    """
    print("Coefficients:")

    # header
    print("  ", end="")
    for i in range(field.bytes_to_elements(len(coefficients))):
        print(f"{i:3}", end="")
    print()
    # values
    print("  ", end="")
    for i in range(field.bytes_to_elements(len(coefficients))):
        print(f"{field.get_value(coefficients, i):3}", end="")
    print()
