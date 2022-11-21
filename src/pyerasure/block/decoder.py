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

from typing import Tuple, Union, Optional
from enum import Enum

from ..finite_field import Binary, Binary4, Binary8, Vector


class Decoder:
    """The block decoder class is used to decode a set of encoded symbols."""

    class SymbolStatus(Enum):
        MISSING = 0
        PARTIALLY_DECODED = 1
        DECODED = 2

    def __init__(
        self,
        field: Union[Binary, Binary4, Binary8],
        symbols: int,
        symbol_bytes: int,
    ):
        """
        The block decoder constructor.

        :param field: the chosen finite field.
        :param symbols: The number of symbols in the block.
        :param symbol_bytes: The size of a symbol in bytes.
        """
        self._field = field
        self._symbols = symbols
        self._symbol_bytes = symbol_bytes
        self._rank = 0
        self._symbols_data: list[Optional[Vector]] = [None] * symbols
        self._coefficients: list[Optional[Vector]] = [None] * symbols
        self._symbol_status = [Decoder.SymbolStatus.MISSING] * symbols

    @property
    def symbols(self) -> int:
        """The number of symbols."""
        return self._symbols

    @property
    def symbol_bytes(self) -> int:
        """The size of a symbol in bytes."""
        return self._symbol_bytes

    @property
    def field(self) -> Union[Binary, Binary4, Binary8]:
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

    def is_symbol_missing(self, index: int) -> bool:
        """
        Check if a symbol is missing.

        :param index: The index of the symbol.
        :return: True if the symbol is missing.
        """
        if index >= self.symbols:
            raise ValueError(f"Invalid symbol index {index}")
        return self._symbol_status[index] == Decoder.SymbolStatus.MISSING

    def is_symbol_pivot(self, index: int) -> bool:
        """
        Check if a symbol is a pivot symbol.

        :param index: The index of the symbol.
        :return: True if the symbol is a pivot symbol.
        """
        if index >= self.symbols:
            raise ValueError(f"Invalid symbol index {index}")
        return self._symbol_status[index] != Decoder.SymbolStatus.MISSING

    def is_symbol_decoded(self, index: int) -> bool:
        """
        Check if a symbol is decoded.

        :param index: The index of the symbol.
        :return: True if the symbol is decoded.
        """
        if index >= self.symbols:
            raise ValueError(f"Invalid symbol index {index}")

        if self._symbol_status[index] != Decoder.SymbolStatus.DECODED:
            # Check coefficients
            if self.__is_coefficients_decoded(index):
                self._symbol_status[index] = Decoder.SymbolStatus.DECODED
                return True
            return False
        else:
            return True

    def symbol_data(self, index: int) -> bytearray:
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        """
        if index >= self.symbols:
            raise ValueError(f"Invalid symbol index {index}")

        return self._symbols_data[index].data

    def block_data(self) -> bytes:
        """
        Get the data of the block.

        :return: The data of the block.
        """

        block_data = bytearray()
        for i in range(self.symbols):
            symbol_data = self.symbol_data(i)
            if symbol_data is None:
                symbol_data = bytearray(self.symbol_bytes)
            block_data.extend(symbol_data)
        return block_data

    def coefficients(self, index: int) -> bytearray:
        """
        Get the coefficients of a symbol.

        :param index: The index of the symbol.
        """
        if index >= self.symbols:
            raise ValueError(f"Invalid symbol index {index}")

        return self._coefficients[index].data

    def decode_symbol(self, symbol_data: bytearray, coefficients: bytearray):
        """
        Feed a coded symbol to the decoder.

        :param symbol: The data of the symbol assumed to be symbol_bytes()
                       bytes in size.
        :param coefficients: The coding coefficients that describe the
                             encoding performed on the symbol.
        """
        self.__decode_symbol(
            Vector(self.field, symbol_data),
            Vector(self.field, coefficients, self.symbols),
        )

    def __decode_symbol(self, symbol_data: Vector, coefficients: Vector):

        pivot_index = None

        # Forwards substitution
        for index, coefficient in coefficients:

            if coefficient == 0:
                continue

            if not self.is_symbol_pivot(index):
                if pivot_index is None:
                    pivot_index = index
                    # Binary fields are already normalized
                    if not self.field.is_binary():
                        # Normalize the coefficients
                        inverted_coefficient = ~coefficient
                        coefficients *= inverted_coefficient
                        symbol_data *= inverted_coefficient
                continue

            coefficients -= self._coefficients[index] * coefficient
            symbol_data -= self._symbols_data[index] * coefficient

        if pivot_index is None:
            return

        self.__store(pivot_index, coefficients, symbol_data)

        # Backward substitution
        for index in range(self.symbols):
            if index == pivot_index:
                continue

            if self.is_symbol_decoded(index):
                continue

            if self.is_symbol_missing(index):
                continue

            coefficient = self._coefficients[index][pivot_index]
            if coefficient == 0:
                continue

            self._coefficients[index] -= coefficients * coefficient
            self._symbols_data[index] -= symbol_data * coefficient

        if self.is_complete():
            # We have decoded all symbols
            self._symbol_status = [Decoder.SymbolStatus.DECODED] * self.symbols

    def decode_systematic_symbol(self, symbol_data: bytearray, index: int):
        """
        Feed a systematic, i.e, un-coded symbol to the decoder.

        :param symbol_data: The data of the symbol assumed to be symbol_bytes()
         bytes in size.
        :param index: The index of the given symbol.
        """
        if index >= self.symbols:
            raise ValueError(f"Invalid symbol index {index}")

        if self.is_symbol_decoded(index):
            return

        if self.is_symbol_pivot(index):
            # Swap decode

            # Extract the existing symbol and coefficients and set the symbol as missing
            symbol_i = self._symbols_data[index]
            coefficients_i = self._coefficients[index]
            self._symbols_data[index] = None
            self._coefficients[index] = None
            self._symbol_status[index] = Decoder.SymbolStatus.MISSING
            self._rank -= 1

            # Subtract the new pivot symbol
            coefficients_i[0] = 0
            symbol_i -= Vector(self.field, symbol_data)

            # Process the new coded symbol: we know that it must
            # contain a larger pivot id than the current (unless it is reduced
            # to all zeroes which is not possible as that would mean it was
            # already decoded).
            self.__decode_symbol(symbol_i, coefficients_i)

        self._rank += 1

        # Store the symbol
        self._symbols_data[index] = Vector(self.field, symbol_data)
        self._coefficients[index] = Vector.allocateCoefficients(
            self.field, self.symbols
        )
        self._coefficients[index][index] = 1
        self._symbol_status[index] = Decoder.SymbolStatus.DECODED

    def recode_symbol(self, coefficients_in: bytes) -> Tuple[bytes, bytearray]:
        """
        Recodes a new symbol based on given the coefficients and current state
        of the decoder.

        :param coefficients_in: These are the coding coefficients.
        :return: The recoded symbol and resulting coefficients.
        """

        symbol_data, coefficients = self.__recode_symbol(
            Vector(self.field, coefficients_in, self.symbols)
        )
        return symbol_data.data, coefficients.data

    def __recode_symbol(self, coefficients_in: Vector) -> Tuple[Vector, Vector]:

        symbol_data = Vector.allocateBytes(self.field, self.symbol_bytes)
        coefficients = Vector.allocateCoefficients(self.field, self.symbols)

        for index, coefficient in coefficients_in:

            if coefficient == 0:
                continue

            assert self.is_symbol_pivot(index)

            coefficients += self._coefficients[index] * coefficient
            symbol_data += self._symbols_data[index] * coefficient

        return symbol_data, coefficients

    def __is_coefficients_decoded(self, index: int):
        """
        Check if the coefficients at the given index are decoded.

        :param index: The index of the coefficients.
        :return: True if the coefficients are decoded, False otherwise.
        """
        coefficients = self._coefficients[index]
        if coefficients is None:
            return False

        for i, coefficient in coefficients:
            if i == index:
                if coefficient != 1:
                    return False

            if coefficient != 0:
                return False

        return True

    def __store(self, index: int, coefficients: Vector, symbol_data: Vector):
        """
        Store the given coefficients and symbol data.

        :param index: The index of the symbol.
        :param coefficients: The coefficients of the symbol.
        :param symbol_data: The data of the symbol.
        """
        if not self.is_symbol_missing(index):
            raise ValueError(f"Symbol {index} is not missing")
        self._symbol_status[index] = Decoder.SymbolStatus.PARTIALLY_DECODED
        self._symbols_data[index] = symbol_data
        self._coefficients[index] = coefficients
        self._rank += 1

    def __str__(self):
        result = []
        for index, coefficients in enumerate(self._coefficients):
            if coefficients is None:
                result.append(f"{index :2d}: None")
            else:
                result.append(f"{index :2d}: {str(coefficients)}")

        return "Decoder({},\n{}\n)".format(self._rank, "\n".join(result))
