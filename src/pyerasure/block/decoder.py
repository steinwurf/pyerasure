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

from typing import Tuple, Union
from enum import Enum

from pyerasure import finite_field


class Decoder:
    """The block decoder class is used to decode a set of encoded symbols."""

    class SymbolStatus(Enum):
        MISSING = 0
        PARTIALLY_DECODED = 1
        DECODED = 2

    def __init__(
        self,
        field: Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8],
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
        self._symbols_data = [None] * symbols
        self._coefficients = [None] * symbols
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
    def field(
        self,
    ) -> Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8]:
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

        return self._symbols_data[index]

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

        return self._coefficients[index]

    def decode_symbol(self, symbol_data: bytearray, coefficients: bytearray):
        """
        Feed a coded symbol to the decoder.

        :param symbol: The data of the symbol assumed to be symbol_bytes()
                       bytes in size.
        :param coefficients: The coding coefficients that describe the
                             encoding performed on the symbol.
        """
        pivot_index = self.__forward_substitute_to_pivot(symbol_data, coefficients)
        if pivot_index is None:
            return
        if not self.field.is_binary():
            self.__normalize(symbol_data, coefficients, pivot_index)
        self.__forward_substitute_from_pivot(symbol_data, coefficients, pivot_index)
        self.__backward_substitute(symbol_data, coefficients, pivot_index)

        # Store coded symbol
        self._symbols_data[pivot_index] = symbol_data
        self._coefficients[pivot_index] = coefficients
        self._symbol_status[pivot_index] = Decoder.SymbolStatus.PARTIALLY_DECODED
        self._rank += 1

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
            self.__swap_decode(symbol_data, index)

        self._rank += 1

        # Store the symbol
        self._symbols_data[index] = symbol_data
        self._coefficients[index] = bytearray(
            self.field.elements_to_bytes(self.symbols)
        )
        self.field.set_value(self.coefficients(index), index, 1)
        self._symbol_status[index] = Decoder.SymbolStatus.DECODED

    def recode_symbol(self, coefficients_in: bytes) -> Tuple[bytes, bytearray]:
        """
        Recodes a new symbol based on given the coefficients and current state
        of the decoder.

        :param coefficients_in: These are the coding coefficients.
        :return: The recoded symbol and resulting coefficients.
        """

        symbol_data = bytearray(self.symbol_bytes)
        coefficients = bytearray(self.field.elements_to_bytes(self.symbols))

        for index in range(self.symbols):

            value = self.field.get_value(coefficients_in, index)

            if value == 0:
                continue

            assert self.is_symbol_pivot(index)

            self.field.vector_multiply_add_into(
                coefficients, self.coefficients(index), value
            )
            self.field.vector_multiply_add_into(
                symbol_data,
                self.symbol_data(index),
                value,
            )
        return symbol_data, coefficients

    def __forward_substitute_to_pivot(
        self, symbol_data: bytearray, coefficients: bytearray
    ) -> int:
        """
        Forward substitute the given symbol to the pivot symbol.

        :param symbol_data: The data of the symbol.
        :param coefficients: The coefficients of the symbol.
        :return: The index of the pivot symbol, or none if no pivot symbol
        """
        for index in range(self.symbols):
            coefficient = self.field.get_value(coefficients, index)

            if coefficient == 0:
                continue

            if not self.is_symbol_pivot(index):
                return index

            self.field.vector_multiply_subtract_into(
                coefficients, self.coefficients(index), coefficient
            )

            self.field.vector_multiply_subtract_into(
                symbol_data, self.symbol_data(index), coefficient
            )

        return None

    def __forward_substitute_from_pivot(
        self, symbol_data: bytearray, coefficients: bytearray, pivot: int
    ):
        """
        Forward substitute the given symbol from the pivot symbol.

        :param symbol_data: The data of the symbol.
        :param coefficients: The coefficients of the symbol.
        :param pivot: The index of the pivot symbol.
        """

        # Start right after the pivot_index position
        for index in range(pivot + 1, self.symbols):
            coefficient = self.field.get_value(coefficients, index)

            if coefficient == 0:
                continue

            if not self.is_symbol_pivot(index):
                continue

            self.field.vector_multiply_subtract_into(
                coefficients, self.coefficients(index), coefficient
            )

            self.field.vector_multiply_subtract_into(
                symbol_data, self.symbol_data(index), coefficient
            )

    def __backward_substitute(
        self, symbol_data: bytearray, coefficients: bytearray, pivot_index: int
    ):
        """
        Backward substitute the given symbol.

        :param symbol_data: The data of the symbol.
        :param coefficients: The coefficients of the symbol.
        :param pivot_index: The index of the pivot symbol.
        """

        # We found a "1" that nobody else had as pivot, we now
        # subtract this packet from other coded packets
        # - if they have a "1" at our pivot position
        for index in range(self.symbols):

            if index == pivot_index:
                # We cannot backward substitute into our self
                continue

            if self.is_symbol_decoded(index):
                # We know that we have no non-zero elements
                # outside the pivot position.
                continue

            if self.is_symbol_missing(index):
                # We do not have a symbol yet here
                continue

            coefficient = self.field.get_value(self.coefficients(index), pivot_index)

            if coefficient == 0:
                continue

            # Update symbol and corresponding vector
            self.field.vector_multiply_subtract_into(
                self.coefficients(index), coefficients, coefficient
            )
            self.field.vector_multiply_subtract_into(
                self.symbol_data(index), symbol_data, coefficient
            )

    def __normalize(self, symbol_data: bytearray, coefficients: bytearray, index: int):
        """
        Normalize the given symbol.

        :param symbol_data: The data of the symbol.
        :param coefficients: The coefficients of the symbol.
        :param index: The index of the symbol.
        """
        coefficient = self.field.get_value(coefficients, index)

        inverted_coefficient = self.field.invert(coefficient)

        self.field.vector_multiply_into(
            coefficients,
            inverted_coefficient,
        )

        self.field.vector_multiply_into(symbol_data, inverted_coefficient)

    def __swap_decode(self, symbol_data: bytearray, index: int):
        """
        Swap the given symbol with an existing coded symbol.

        :param symbol_data: The data of the symbol.
        :param index: The index of the symbol.
        """
        # extract symbol and coefficients and set the symbol as missing
        symbol_i = self.symbol_data(index)
        coefficients_i = self.coefficients(index)
        self._symbol_status[index] = Decoder.SymbolStatus.MISSING
        self._rank -= 1

        # Subtract the new pivot symbol
        self.field.set_value(coefficients_i, index, 0)
        # Note: add is the same as subtract
        self.field.vector_add_into(symbol_i, symbol_data)

        # Process the new coded symbol: we know that it must
        # contain a larger pivot id than the current (unless it is reduced
        # to all zeroes).
        self.decode_symbol(symbol_i, coefficients_i)

    def __is_coefficients_decoded(self, index: int):
        """
        Check if the coefficients at the given index are decoded.

        :param index: The index of the coefficients.
        :return: True if the coefficients are decoded, False otherwise.
        """
        coefficients = self.coefficients(index)
        if coefficients is None:
            return False

        for i in range(self.symbols):
            if i == index:
                continue

            if self.field.get_value(coefficients, i) != 0:
                return False

        return True
