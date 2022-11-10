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
import pyerasure.slide
import pyerasure.slide.generator
import pyerasure.finite_field


class TestSlideGenerators(unittest.TestCase):
    def test_random_uniform_coefficients_bytes(self):
        args = [
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(0, 0), 0),
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(0, 1), 1),
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(0, 8), 1),
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(0, 9), 2),
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(1, 9), 2),
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(8, 9), 1),
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(9, 9), 0),
            (pyerasure.finite_field.Binary(), pyerasure.slide.Range(9, 10), 1),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(0, 0), 0),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(0, 1), 1),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(0, 2), 1),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(0, 3), 2),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(1, 3), 2),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(4, 5), 1),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(4, 6), 1),
            (pyerasure.finite_field.Binary4(), pyerasure.slide.Range(6, 7), 1),
            (pyerasure.finite_field.Binary8(), pyerasure.slide.Range(0, 0), 0),
            (pyerasure.finite_field.Binary8(), pyerasure.slide.Range(0, 1), 1),
            (pyerasure.finite_field.Binary8(), pyerasure.slide.Range(0, 2), 2),
            (pyerasure.finite_field.Binary8(), pyerasure.slide.Range(1, 2), 1),
            (pyerasure.finite_field.Binary8(), pyerasure.slide.Range(2, 2), 0),
            (pyerasure.finite_field.Binary8(), pyerasure.slide.Range(2, 3), 1),
        ]
        for arg in args:
            with self.subTest(arg):
                field, window, expected_bytes = arg
                print(f"{field}, {window} {expected_bytes}")
                self.random_uniform_coefficients_bytes(field, window, expected_bytes)

    def random_uniform_coefficients_bytes(self, field, window, expected_bytes):
        generator = pyerasure.slide.generator.RandomUniform(field)
        self.assertEqual(expected_bytes, generator.coefficients_bytes(window))

    def test_random_uniform_simple(self):
        fields = [
            pyerasure.finite_field.Binary(),
            pyerasure.finite_field.Binary4(),
            pyerasure.finite_field.Binary8(),
        ]
        for field in fields:
            with self.subTest(field):
                self.random_uniform_simple(field)

    def random_uniform_simple(self, field):
        window = pyerasure.slide.Range(0, 40)

        generator = pyerasure.slide.generator.RandomUniform(field)
        self.assertEqual(field, generator.field)
        generator.set_seed(0)
        coefficients1 = generator.generate(window)
        generator.set_seed(1)
        coefficients2 = generator.generate(window)
        self.assertNotEqual(coefficients1, coefficients2)
        generator.set_seed(0)
        coefficients3 = generator.generate(window)
        self.assertEqual(coefficients1, coefficients3)


if __name__ == "__main__":
    unittest.main()
