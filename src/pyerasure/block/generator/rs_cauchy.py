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

from typing import Union, Tuple
from ...finite_field import Binary4, Binary8


class RSCauchy:
    """
    A Reed-Solomon-Cauchy coefficients generator
    """

    def __init__(self, field: Union[Binary4, Binary8], symbols):
        """
        The Reed-Solomon-Cauchy generator constructor.

        :param field: The chosen finite field.
        :param symbols: The number of symbols.
        """
        self._field = field

        if symbols >= self.field.max_value:
            raise ValueError(f"symbols must be less than {self.field.max_value}")

        self._symbols = symbols
        self._next_repair_symbol = 0
        self._matrix = []
        for i in range(self.field.max_value):
            self._matrix.append(bytearray(self.field.max_value))
            xi = self.field.max_value - i
            for j in range(self.field.max_value):
                result = self.field.add(xi, j)
                if result != 0:
                    self._matrix[i][j] = self.field.invert(result)

    @property
    def symbols(self) -> int:
        """The number of symbols."""
        return self._symbols

    @property
    def field(self) -> Union[Binary4, Binary8]:
        """The chosen finite field."""
        return self._field

    @property
    def repair_symbols(self) -> int:
        """Return the number of repair symbols supported by this generator."""
        return self.field.max_value - self.symbols

    def remaining_repair_symbols(self):
        """The number of remaining repair symbols."""
        return self.repair_symbols - self._next_repair_symbol

    def generate(self) -> Tuple[bytes, int]:
        """
        Generates the coefficients.

        :return: A tuple containing the coefficients and the index of the generated coefficients.
                 The index can be used with RSCauchy.generate_specific() to recreate the coefficients
                 at a later time.
        """
        if self._next_repair_symbol >= self.repair_symbols:
            raise ValueError("no more repair symbols")
        index = self._next_repair_symbol
        coefficients = self.generate_specific(index)
        self._next_repair_symbol -= 1
        return coefficients, index

    def generate_specific(self, index: int) -> bytes:
        """
        Generate a specific set of coefficients.

        :param index: The index of the coefficients to generate.
                      The index must be less than or equal to RSCauchy.repair_symbols
        :return: The coefficients.
        """
        if index >= self.repair_symbols:
            raise ValueError("index out of range")
        coefficients = bytearray(self.field.bytes_to_elements(self.symbols))
        for i in range(self.symbols):
            coefficients[i] = self._matrix[index][i]
        return bytes(coefficients)
