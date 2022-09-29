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
import pyerasure
import pyerasure.generator


class TestBlockEncodeDecode(unittest.TestCase):
    def test_encode_decode_simple_random_uniform(self):
        random_uniform_fields = [pyerasure.finite_field.Binary]

        for field in random_uniform_fields:
            with self.subTest(field):
                self.encode_decode_simple_random_uniform(field)

    def encode_decode_simple_random_uniform(self, field):

        symbol_bytes = 1400
        symbols = 150

        encoder = pyerasure.Encoder(field, symbols, symbol_bytes)
        self.assertEqual(field, encoder.field)

        self.assertEqual(symbols, encoder.symbols)
        self.assertEqual(symbol_bytes, encoder.symbol_bytes)

        decoder = pyerasure.Decoder(field, symbols, symbol_bytes)
        self.assertEqual(field, decoder.field)
        self.assertEqual(symbols, decoder.symbols)
        self.assertEqual(symbol_bytes, decoder.symbol_bytes)

        generator = pyerasure.generator.RandomUniform(field, encoder.symbols)
        self.assertEqual(field, generator.field)
        self.assertEqual(symbols, generator.symbols)
        generator.set_seed(0)

        data_in = bytearray(os.urandom(encoder.block_bytes))
        encoder.set_symbols(data_in)

        systematic_index = 0

        loss_probability = 10

        iterations = symbols * 2

        while not decoder.is_complete():
            iterations -= 1

            self.assertNotEqual(0, iterations)

            if encoder.rank > systematic_index:

                old_rank = decoder.rank
                index = systematic_index
                systematic_index += 1
                symbol = encoder.symbol_data(index)

                if random.randint(0, 100) < loss_probability:

                    continue

                else:
                    decoder.decode_systematic_symbol(symbol, index)
                    self.assertNotEqual(old_rank, decoder.rank)

            else:

                old_rank = decoder.rank
                coefficients = generator.generate()
                symbol = encoder.encode_symbol(coefficients)

                if random.randint(0, 100) < loss_probability:

                    continue

                else:

                    decoder.decode_symbol(symbol, coefficients)

        self.assertEqual(data_in, data_out)


if __name__ == "__main__":
    unittest.main()
