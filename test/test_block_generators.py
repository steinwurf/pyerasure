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
import pyerasure.block.generator
import pyerasure.finite_field


class TestBlockGenerators(unittest.TestCase):
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

        symbols = 40

        generator = pyerasure.block.generator.RandomUniform(field, symbols)
        self.assertEqual(field, generator.field)
        self.assertEqual(symbols, generator.symbols)
        generator.set_seed(0)
        coefficients1 = generator.generate()
        generator.set_seed(1)
        coefficients2 = generator.generate()
        self.assertNotEqual(coefficients1, coefficients2)
        generator.set_seed(0)
        coefficients3 = generator.generate()
        self.assertEqual(coefficients1, coefficients3)


if __name__ == "__main__":
    unittest.main()
