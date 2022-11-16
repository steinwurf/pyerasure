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


import os
import random
import unittest
import pyerasure.slide
import pyerasure.slide.generator
import pyerasure.finite_field


class TestSlideEncodeDecode(unittest.TestCase):
    def test_encode_decode_systematic(self):
        random_uniform_fields = [
            pyerasure.finite_field.Binary(),
            pyerasure.finite_field.Binary4(),
            pyerasure.finite_field.Binary8(),
        ]

        for field in random_uniform_fields:
            with self.subTest(field):
                self.encode_decode_systematic(field)

    def encode_decode_systematic(self, field):
        max_symbol_bytes = 30

        encoder = pyerasure.slide.Encoder(field, max_symbol_bytes)
        self.assertEqual(field, encoder.field)

        self.assertEqual(max_symbol_bytes, encoder.max_symbol_bytes)

        decoder = pyerasure.slide.Decoder(field, max_symbol_bytes)
        self.assertEqual(field, decoder.field)
        self.assertEqual(max_symbol_bytes, decoder.max_symbol_bytes)

        for index in range(40):

            if index not in encoder.stream():
                symbol = bytearray(os.urandom(encoder.max_symbol_bytes))
                encoder.push_symbol(symbol)

            symbol = encoder.symbol_data(index)
            while index not in decoder.stream():
                decoder.push_symbol()

            decoder.decode_systematic_symbol(symbol, index)

        for index in decoder.stream():
            self.assertEqual(encoder.symbol_data(index), decoder.symbol_data(index))

    def test_encode_decode_mixed(self):
        random_uniform_fields = [
            pyerasure.finite_field.Binary(),
            pyerasure.finite_field.Binary4(),
            pyerasure.finite_field.Binary8(),
        ]

        for field in random_uniform_fields:
            with self.subTest(field):
                self.encode_decode_mixed(field)

    def encode_decode_mixed(self, field):
        max_symbol_bytes = 30

        encoder = pyerasure.slide.Encoder(field, max_symbol_bytes)
        self.assertEqual(field, encoder.field)
        self.assertEqual(max_symbol_bytes, encoder.max_symbol_bytes)

        decoder = pyerasure.slide.Decoder(field, max_symbol_bytes)
        self.assertEqual(field, decoder.field)
        self.assertEqual(max_symbol_bytes, decoder.max_symbol_bytes)

        generator = pyerasure.slide.generator.RandomUniform(field)
        self.assertEqual(field, generator.field)

        symbols = []
        loss_probability = 10
        for index in range(40):
            encoder.push_symbol(bytearray(os.urandom(encoder.max_symbol_bytes)))
            if len(encoder.stream()) > 10:
                symbols.append(encoder.pop_symbol())
            symbol = encoder.symbol_data(index)

            if random.randint(0, 100) >= loss_probability:
                while index not in decoder.stream():
                    decoder.push_symbol()
                decoder.decode_systematic_symbol(symbol, index)
            else:
                # lost
                pass

            if index % 8 == 0:
                window = encoder.stream()
                coefficients = generator.generate(window)
                symbol = encoder.encode_symbol(window, coefficients)

                if random.randint(0, 100) >= loss_probability:
                    while window not in decoder.stream():
                        decoder.push_symbol()
                    decoder.decode_symbol(symbol, window, bytearray(coefficients))
                else:
                    # lost
                    pass

        for index in encoder.stream():
            symbols.append(encoder.pop_symbol())

        for index in decoder.stream():
            if decoder.is_symbol_decoded(index):
                self.assertEqual(symbols[index], decoder.symbol_data(index))

    # def test_encode_decode_no_systematic(self):
    #     random_uniform_fields = [
    #         pyerasure.finite_field.Binary(),
    #         pyerasure.finite_field.Binary4(),
    #         pyerasure.finite_field.Binary8(),
    #     ]

    #     for field in random_uniform_fields:
    #         with self.subTest(field):
    #             self.encode_decode_no_systematic(field)

    # def encode_decode_no_systematic(self, field):

    #     symbol_bytes = 300
    #     symbols = 41

    #     encoder = pyerasure.slide.Encoder(field, symbols, symbol_bytes)
    #     decoder = pyerasure.slide.Decoder(field, symbols, symbol_bytes)
    #     generator = pyerasure.slide.generator.RandomUniform(field, encoder.symbols)

    #     data_in = bytearray(os.urandom(encoder.slide_bytes))
    #     encoder.set_symbols(data_in)

    #     iterations = symbols * 2

    #     while not decoder.is_complete():
    #         iterations -= 1
    #         self.assertNotEqual(0, iterations)

    #         coefficients = generator.generate()
    #         symbol = encoder.encode_symbol(coefficients)
    #         decoder.decode_symbol(symbol, bytearray(coefficients))

    #     for index in range(symbols):
    #         self.assertEqual(encoder.symbol_data(index), decoder.symbol_data(index))
    #     data_out = decoder.slide_data()
    #     self.assertEqual(len(data_in), len(data_out))
    #     self.assertEqual(data_in, data_out)


if __name__ == "__main__":
    unittest.main()
