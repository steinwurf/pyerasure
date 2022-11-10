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


class TestFiniteField(unittest.TestCase):
    def test_elements_to_bytes(self):
        args = [
            (pyerasure.finite_field.Binary(), 0, 0),
            (pyerasure.finite_field.Binary(), 1, 1),
            (pyerasure.finite_field.Binary(), 8, 1),
            (pyerasure.finite_field.Binary(), 9, 2),
            (pyerasure.finite_field.Binary4(), 0, 0),
            (pyerasure.finite_field.Binary4(), 1, 1),
            (pyerasure.finite_field.Binary4(), 2, 1),
            (pyerasure.finite_field.Binary4(), 3, 2),
            (pyerasure.finite_field.Binary4(), 4, 2),
            (pyerasure.finite_field.Binary4(), 5, 3),
            (pyerasure.finite_field.Binary8(), 0, 0),
            (pyerasure.finite_field.Binary8(), 1, 1),
            (pyerasure.finite_field.Binary8(), 2, 2),
            (pyerasure.finite_field.Binary8(), 3, 3),
        ]
        for arg in args:
            with self.subTest(arg):
                field, elements, expected_bytes = arg
                print(f"{field}, {elements} {expected_bytes}")
                self.random_elements_to_bytes(field, elements, expected_bytes)

    def random_elements_to_bytes(self, field, elements, expected_bytes):
        self.assertEqual(expected_bytes, field.elements_to_bytes(elements))


if __name__ == "__main__":
    unittest.main()
