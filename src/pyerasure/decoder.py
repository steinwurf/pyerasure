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

from enum import Enum

from pyerasure import finite_field


class Decoder:
    """The decoder class is used to decode a set of encoded symbols."""

    class SymbolStatus(Enum):
        MISSING = 0
        PARTIALLY_DECODED = 1
        DECODED = 2

    def __init__(self, field: finite_field.Binary, symbols: int, symbol_bytes: int):
        """
        The decoder constructor.

        :param field: the chosen finite field.
        :param symbols: The number of symbols.
        :param symbol_bytes: The size of a symbol in bytes.
        """
        self._field = field
        self._symbols = symbols
        self._symbol_bytes = symbol_bytes
        self._rank = 0
        self._symbols_data = [None] * symbols
        self._coefficients = [None] * symbols
        self.symbol_status = [Decoder.SymbolStatus.MISSING] * symbols

    @property
    def symbols(self) -> int:
        """The number of symbols."""
        return self._symbols

    @property
    def symbol_bytes(self) -> int:
        """The size of a symbol in bytes."""
        return self._symbol_bytes

    @property
    def field(self):
        """The chosen finite field."""
        return self._field

    @property
    def block_bytes(self) -> int:
        """The size of the block in bytes."""
        return self._symbols * self._symbol_bytes

    @property
    def rank(self) -> int:
        """The rank of the decoding matrix."""
        return self._rank

    def is_complete(self) -> bool:
        """
        Check if the decoder is complete.

        :return: True if the decoder is complete.
        """
        return self._rank == self._symbols

    def symbol_data(self, index: int) -> bytes:
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        """
        if index >= self._symbols:
            raise ValueError(f"Invalid symbol index {index}")

        return self._symbols_data[index]

    def decode_symbol(self, symbol_data: bytearray, coefficients: bytearray):
        """
        Feed a coded symbol to the decoder.

        :param symbol: The data of the symbol assumed to be symbol_bytes()
                       bytes in size.
        :param coefficients: The coding coefficients that describe the
                             encoding performed on the symbol.
        """
        pass

    def decode_systematic_symbol(self, symbol_data: bytearray, index: int):
        """
        Feed a systematic, i.e, un-coded symbol to the decoder.

        :param symbol_data: The data of the symbol assumed to be symbol_bytes()
         bytes in size.
        :param index: The index of the given symbol.
        """
        if index >= self._symbols:
            raise ValueError(f"Invalid symbol index {index}")

        if self.symbol_status[index] == Decoder.SymbolStatus.DECODED:
            return

        if self.symbol_status[index] == Decoder.SymbolStatus.PARTIALLY_DECODED:
            self.__swap_decode(symbol_data, index)

        if self.symbol_status[index] == Decoder.SymbolStatus.MISSING:
            self._symbols_data[index] = symbol_data
            self._coefficients[index] = bytearray(self._symbols)
            self.field.set_value(self._coefficients[index], index, 1)
            self.symbol_status[index] = Decoder.SymbolStatus.DECODED
            self._rank += 1

    def __swap_decode(self, symbol_data: bytearray, index: int):
        pass

    def recode_symbol(self, coefficients: bytes):
        """
        Recodes a new symbol based on given the coeffcients and current state
        of the decoder.

        :param coefficients: These are the coding coefficients.
        :return: The recoded symbol and resulting coefficients.
        """
        return None, None

    def is_symbol_pivot(self, index: int) -> bool:
        """
        Check if a symbol is a pivot symbol.

        :param index: The index of the symbol.
        :return: True if the symbol is a pivot symbol.
        """
        return self.symbol_status[index] != Decoder.SymbolStatus.MISSING

    def is_symbol_decoded(self, index: int) -> bool:
        """
        Check if a symbol is decoded.

        :param index: The index of the symbol.
        :return: True if the symbol is decoded.
        """
        return self.symbol_status[index] == Decoder.SymbolStatus.DECODED
