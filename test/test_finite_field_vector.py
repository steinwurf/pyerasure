#!/usr/bin/env python
# encoding: utf-8

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


import unittest
import pyerasure.finite_field


def b(string: str) -> bytearray:
    """
    Convert a string of 0s and 1s to a bytearray.

    :param string: The string of 0s and 1s.
    :return: The bytearray.
    """

    # strip spaces
    string = string.replace(" ", "")
    return bytearray(int(string, 2).to_bytes((len(string) + 7) // 8, "big"))


class TestFiniteFieldVector(unittest.TestCase):
    def test_binary_add(self):
        args = [
            # (
            #     (b("0000 0000"), 0),
            #     (b("0000 0000"), 0),
            #     (b("0000 0000"), 0),
            # ),
            # (
            #     (b("1010 0101"), 0),
            #     (b("1111 1111"), 0),
            #     (b("0101 1010"), 0),
            # ),
            # (
            #     (b("1100 0011"), 0),
            #     (b("1101 1011"), 0),
            #     (b("0001 1000"), 0),
            # ),
            # (
            #     (b("0110 0001"), 1),
            #     (b("0011 0110"), 2),
            #     (b("0101 0111"), 1),
            # ),
            (
                (b("0110 0001"), 9),
                (b("0011 0110"), 10),
                (b("0101 0111"), 9),
            ),
            # (
            #     (b("0110 0001"), 17),
            #     (b("0011 0110"), 18),
            #     (b("0101 0111"), 17),
            # ),
            # (
            #     (b("1100 0011 1010 0110"), 0),
            #     (b("1101 1011"), 0),
            #     (b("0001 1000 1010 0110 "), 0),
            # ),
            # (
            #     (b("1100 0011 1010 0110"), 0),
            #     (b("          1101 1011"), 8),
            #     (b("1100 0011 0111 1101 "), 0),
            # ),
        ]
        for arg in args:
            with self.subTest(arg):
                (x, xOffset), (y, yOffset), (expectation, expectationOffset) = arg
                print(f"{x} + {y} = {expectation}")
                self.binary_add(
                    pyerasure.finite_field.Vector(
                        pyerasure.finite_field.Binary(), x, offset=xOffset
                    ),
                    pyerasure.finite_field.Vector(
                        pyerasure.finite_field.Binary(), y, offset=yOffset
                    ),
                    pyerasure.finite_field.Vector(
                        pyerasure.finite_field.Binary(),
                        expectation,
                        offset=expectationOffset,
                    ),
                )

    def binary_add(self, x, y, expectation):
        self.assertEqual(expectation, x + y)
        self.assertEqual(expectation, y + x)


if __name__ == "__main__":
    unittest.main()
