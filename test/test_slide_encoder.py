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
import pyerasure.utils
import pyerasure.slide.generator
import pyerasure.finite_field


class TestSlideEncoder(unittest.TestCase):
    def test_encoder(self):
        fields = [
            pyerasure.finite_field.Binary(),
            pyerasure.finite_field.Binary4(),
            pyerasure.finite_field.Binary8(),
        ]

        for field in fields:
            with self.subTest(field):
                self.encoder(field)

    def encoder(self, field):

        max_symbol_bytes = 300

        generator = pyerasure.slide.generator.RandomUniform(field)
        self.assertEqual(field, generator.field)

        encoder = pyerasure.slide.Encoder(field, max_symbol_bytes)
        self.assertEqual(field, encoder.field)
        self.assertEqual(max_symbol_bytes, encoder.max_symbol_bytes)
        self.assertEqual(pyerasure.slide.Range(0, 0), encoder.stream())

        encoder.push_symbol(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF")
        encoder.push_symbol(b"\x01\x01")
        encoder.push_symbol(b"\x00\x00\x02\x02")
        encoder.push_symbol(b"\x00\x00\x00\x00\x03\x03")
        encoder.push_symbol(b"\x00\x00\x00\x00\x00\x00\x04\x04")

        self.assertEqual(pyerasure.slide.Range(0, 5), encoder.stream())

        self.assertEqual(
            b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF", encoder.symbol_data(0)
        )
        self.assertEqual(b"\x01\x01", encoder.symbol_data(1))
        symbol = encoder.pop_symbol()
        self.assertEqual(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF", symbol)
        self.assertEqual(pyerasure.slide.Range(1, 5), encoder.stream())

        self.assertEqual(b"\x01\x01", encoder.symbol_data(1))

        window = encoder.stream()
        frame = pyerasure.utils.to_frame(encoder.field.elements_per_byte, window)
        coefficients = bytearray(generator.coefficients_bytes(window))

        for i in frame:
            if i in window:
                encoder.field.set_value(
                    coefficients, pyerasure.utils.relative_index(frame, i), 1
                )

        encoded = encoder.encode_symbol(window, coefficients)
        self.assertEqual(8, len(encoded))
        self.assertEqual(b"\x01\x01\x02\x02\x03\x03\x04\x04", encoded)


if __name__ == "__main__":
    unittest.main()
