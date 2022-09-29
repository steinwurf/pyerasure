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


class Encoder:
    """The encoder class is used to encode a set of symbols."""

    def __init__(self, field, symbols, symbol_bytes):
        """
        The encoder constructor.

        :param field: the chosen finite field.
        :param symbols: The number of symbols.
        :param symbol_bytes: The size of a symbol in bytes.
        """
        self.field = field
        self.symbols = symbols
        self.symbol_bytes = symbol_bytes
        self._rank = 0

    @property
    def symbols(self):
        """The number of symbols."""
        return self.symbols

    @property
    def symbol_bytes(self):
        """The size of a symbol in bytes."""
        return self.symbol_bytes

    @property
    def field(self):
        """The chosen finite field."""
        return self.field

    @property
    def block_bytes(self):
        """The size of the block in bytes."""
        return self.symbols * self.symbol_bytes

    @property
    def rank(self):
        """The rank of the encoding matrix, i.e., the number of symbols."""
        return self._rank

    def set_symbol(self, index, data):
        """
        Set a symbol.

        :param index: The index of the symbol.
        :param data: The data of the symbol.
        """
        pass

    def is_symbol_set(self, index):
        """
        Check if a symbol is set.

        :param index: The index of the symbol.
        :return: True if the symbol set.
        """
        return False

    def symbol_data(self, index):
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        :return: The data of the symbol.
        """
        pass

    def encode_symbol(self, coefficients):
        """
        Encode a symbol based on the given coefficients.

        :param coefficients: The coding coefficients that describe the
                             encoding.
        :return: The encoded symbol.
        """
        pass
