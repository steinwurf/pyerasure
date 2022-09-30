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

from typing import Union
import pyerasure
import random
from .. import finite_field


class RandomUniform:
    """
    Uniform random block generator.
    """

    def __init__(
        self,
        field: Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8],
        symbols,
    ) -> None:
        """
        The random uniform block generator constructor.

        :param field: The chosen finite field.
        :param symbols: The number of symbols.
        """
        self._field = field
        self._symbols = symbols
        self.random = random.Random()

    @property
    def symbols(self) -> int:
        """The number of symbols."""
        return self._symbols

    @property
    def field(
        self,
    ) -> Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8]:
        """The chosen finite field."""
        return self._field

    def generate(self) -> bytes:
        """
        Generate the coefficients.
        """
        return self.generate_partial(self.symbols)

    def generate_partial(self, rank: int) -> bytes:
        """
        Generate the coefficients.
        """
        bytes_to_generate = self.field.elements_to_bytes(rank)
        coefficients = bytearray(
            self.random.getrandbits(8) for _ in range(bytes_to_generate)
        )

        overshoot = rank % 8
        # clear overshoot bits
        if overshoot != 0:
            coefficients[-1] &= (1 << overshoot) - 1
        return bytes(coefficients)

    def generate_recode(self, decoder: pyerasure.Decoder) -> bytes:
        """
        Generate coefficients based on the decoder state.

        :param decoder: The decoder to query for the current symbol state.
        """
        if decoder.rank == 0:
            raise ValueError("Cannot recode with rank 0")
        if decoder.symbols != self.symbols:
            raise ValueError("Decoder symbols do not match generator symbols")
        coefficients = bytearray(self.generate())
        for i in range(decoder.symbols):
            if not decoder.is_symbol_pivot(i):
                self.field.set_value(coefficients, i, 0)
        return bytes(coefficients)

    def set_seed(self, seed: int):
        """
        Set the state of the coefficient generator. The coefficient generator
        will always produce the same set of coefficients for a given seed.

        :param seed: The seed that will set the state of the generator.
        """
        self.random.seed(seed)
