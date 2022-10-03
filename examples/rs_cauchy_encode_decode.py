#!/usr/bin/env python
# encoding: utf-8

# License for Commercial Usage
# Distributed under the "KODO EVALUATION LICENSE 1.3"
# Licensees holding a valid commercial license may use this project in
# accordance with the standard license agreement terms provided with the
# Software (see accompanying file LICENSE.rst or
# https://www.steinwurf.com/license), unless otherwise different terms and
# conditions are agreed in writing between Licensee and Steinwurf ApS in which
# case the license will be regulated by that separate written agreement.
# License for Non-Commercial Usage
# Distributed under the "KODO RESEARCH LICENSE 1.2"
# Licensees holding a valid research license may use this project in accordance
# with the license agreement terms provided with the Software
# See accompanying file LICENSE.rst or https://www.steinwurf.com/license

import os
import random

import pyerasure
import pyerasure.finite_field
import pyerasure.generator


def main():
    """
    Simple example showing how to encode and decode a block
    of memory using a Cauchy Reed Solomon code.
    """

    # Pick the finite field to use for the encoding and decoding.
    field = pyerasure.finite_field.Binary8()

    # Pick the number of symbols to encode/decode.
    symbols = 40

    # Pick the size of each symbol in bytes
    symbol_bytes = 1400

    # Create an encoder and decoder. The encoder and decoder must be created
    # identically to be compatible.
    encoder = pyerasure.Encoder(field, symbols, symbol_bytes)
    decoder = pyerasure.Decoder(field, symbols, symbol_bytes)

    # The generator must similarly be created based on the encoder/decoder.
    generator = pyerasure.generator.RSCauchy(field, symbols)

    # Allocate some data to encode. In this case we make a buffer
    # with the same size as the encoder's block size (the max.
    # amount a single encoder can encode)
    # Just for fun - fill data_in with random data
    data_in = bytearray(os.urandom(encoder.block_bytes))

    # Assign the data buffer to the encoder so that we may start
    # to produce encoded symbols from it
    encoder.set_symbols(data_in)

    # Keep track of the number of systematic symbols
    systematic_index = 0

    # Lose packets with 10% probability
    loss_probability = 10

    while not decoder.is_complete():

        if encoder.rank > systematic_index:

            index = systematic_index
            systematic_index += 1
            symbol = encoder.symbol_data(index)

            # Drop packet based on loss probability
            if random.randint(0, 100) < loss_probability:
                print(" - lost")
            else:
                decoder.decode_systematic_symbol(symbol, index)
                print(f" - decoded, rank now {decoder.rank}")

        elif generator.remaining_repair_symbols != 0:

            coefficients, index = generator.generate()
            symbol = encoder.encode_symbol(coefficients)

            # Drop packet based on loss probability
            if random.randint(0, 100) < loss_probability:
                print(" - lost")
            else:
                coefficients = generator.generate_specific(index)
                decoder.decode_symbol(symbol, bytearray(coefficients))
                print(f" - decoded, rank now {decoder.rank}")
        else:
            print("Data was not decoded. No more repair available.")
            return

    if data_in != decoder.block_data():
        print("Data was not decoded correctly. Something went wrong")
    else:
        print("Decoding was successful. Yay!")


if __name__ == "__main__":
    main()
