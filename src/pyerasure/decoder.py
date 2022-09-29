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


class Decoder:
    """The decoder class is used to decode a set of encoded symbols."""

    def __init__(self, field, symbols, symbol_bytes):
        """
        The decoder constructor.

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
        """The rank of the decoding matrix."""
        return self._rank

    def is_complete(self):
        """
        Check if the decoder is complete.

        :return: True if the decoder is complete.
        """
        return self.rank == self.symbols

    def symbol_data(self, index):
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        """
        pass

    def decode_symbol(self, symbol, coefficients):
        """
        Feed a coded symbol to the decoder.

        :param symbol: The data of the symbol assumed to be symbol_bytes()
                       bytes in size.
        :param coefficients: The coding coefficients that describe the
                             encoding performed on the symbol.
        """
        pass

    def decode_systematic_symbol(self, symbol, index):
        """
        Feed a systematic, i.e, un-coded symbol to the decoder.

        :param symbol: The data of the symbol assumed to be symbol_bytes()
         bytes in size.
        :param index: The index of the given symbol.
        """
        pass

    def recode_symbol(self, coefficients):
        """
        Recodes a new symbol based on given the coeffcients and current state of the decoder.

        :param coefficients: These are the coding coefficients.
        :return: The recoded symbol and resulting coefficients.
        """
        return None, None

    def is_symbol_pivot(self, index):
        """
        Check if a symbol is a pivot symbol.

        :param index: The index of the symbol.
        :return: True if the symbol is a pivot symbol.
        """
        return False

    def is_symbol_decoded(self, index):
        """
        Check if a symbol is decoded.

        :param index: The index of the symbol.
        :return: True if the symbol is decoded.
        """
        return False
