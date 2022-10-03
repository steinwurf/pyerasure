Quick Start
===========

PyErasure is a pure python implementation of the erasure coding.
This means it's installation is very easy.
Just install the package with pip::

    python3 -m pip install pyerasure

Then you can use it in your python code::

    import os
    import pyerasure
    import pyerasure.finite_field
    import pyerasure.generator

    field = pyerasure.finite_field.Binary8()
    encoder = pyerasure.Encoder(
        field=field,
        symbols=15,
        symbol_bytes=140)
    decoder = pyerasure.Decoder(
        field=field,
        symbols=15,
        symbol_bytes=140)

    generator = pyerasure.generator.RandomUniform(
        field=field,
        symbols=encoder.symbols)

    data_in = bytearray(os.urandom(encoder.block_bytes))
    encoder.set_symbols(data_in)

    while not decoder.is_complete():
        coefficients = generator.generate()
        symbol = encoder.encode_symbol(coefficients)
        decoder.decode_symbol(symbol, bytearray(coefficients))

    assert data_in == decoder.block_data()
    print("Success!")
