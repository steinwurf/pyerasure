Quick Start
===========

PyErasure is a pure python implementation of the erasure coding.
This means its installation is very easy.

1. Obtain a Steinwurf ApS research license (see https://www.steinwurf.com/license/)
2. Setup your Github SSH key (see https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
3. Install the ``pyerasure`` tool using ``pip`` and ``git/ssh``::

      python3 -m pip install git+ssh://git@github.com/steinwurf/pyerasure@[TAG]

   .. note::

      The ``[TAG]`` should be replaced with the desired version or checksum
      of the tool.


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
