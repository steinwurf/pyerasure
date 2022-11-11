# License for Commercial Usage
# Distributed under the "PYERASURE EVALUATION LICENSE 1.3"
# Licensees holding a valid commercial license may use this project in
# accordance with the standard license agreement terms provided with the
# Software (see accompanying file LICENSE.rst or
# https:#www.steinwurf.com/license), unless otherwise different terms and
# conditions are agreed in writing between Licensee and Steinwurf ApS in which
# case the license will be regulated by that separate written agreement.
#
# License for Non-Commercial Usage
# Distributed under the "PYERASURE RESEARCH LICENSE 1.2"
# Licensees holding a valid research license may use this project in accordance
# with the license agreement terms provided with the Software
# See accompanying file LICENSE.rst or https:#www.steinwurf.com/license

from typing import Tuple, Union, Optional
from enum import Enum

from pyerasure import finite_field
from pyerasure.range import Range
from pyerasure import utils


class Decoder:
    """The sliding window decoder used to decode a continueous stream of encoded symbols."""

    class SymbolStatus(Enum):
        MISSING = 0
        PARTIALLY_DECODED = 1
        DECODED = 2

    def __init__(
        self,
        field: Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8],
        max_symbol_bytes: int,
    ):
        """
        The decoder constructor.

        :param field: the chosen finite field.
        :param max_symbol_bytes: The maximum size of a symbol in bytes.
        """
        self._field = field
        self._max_symbol_bytes = max_symbol_bytes
        self._stream = Range(0, 0)
        self._symbols_data: list[Optional[bytearray]] = []
        """The data of the symbols."""

        self._coefficients: list[Optional[bytearray]] = []
        """The coefficients as bytearrays."""

        self._coefficients_offsets: list[Optional[int]] = []
        """The offset of the coefficients, in symbols."""

        self._symbol_status: list[Optional[Decoder.SymbolStatus]] = []
        """The status of the symbols."""

    @property
    def max_symbol_bytes(self) -> int:
        """The maximum size of a symbol in bytes."""
        return self._max_symbol_bytes

    @property
    def field(
        self,
    ) -> Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8]:
        """The chosen finite field."""
        return self._field

    def stream(self) -> Range:
        """The stream range."""
        return self._stream

    def push_symbol(self):
        """
        Push a symbol into the decoder.

        :param index: The index of the symbol.
        :param symbol_data: The data of the symbol.
        :param coefficients: The coefficients of the symbol.
        """
        self._symbols_data.append(None)
        self._coefficients.append(None)
        self._coefficients_offsets.append(None)
        self._symbol_status.append(Decoder.SymbolStatus.MISSING)
        self.stream().push()

    def pop_symbol(self) -> Tuple[int, bytearray]:
        """
        Pop a symbol from the decoder.

        :return: The symbol data.
        """
        if self.stream().empty():
            raise ValueError("Empty stream")

        self.stream().pop()
        self._coefficients.pop(0)
        self._coefficients_offsets.pop(0)
        self._symbol_status.pop(0)
        return self._symbols_data.pop(0)

    def is_symbol_missing(self, index: int) -> bool:
        """
        Check if a symbol is missing.

        :param index: The index of the symbol.
        :return: True if the symbol is missing.
        """

        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        return (
            self._symbol_status[utils.relative_index(self.stream(), index)]
            == Decoder.SymbolStatus.MISSING
        )

    def is_symbol_pivot(self, index: int) -> bool:
        """
        Check if a symbol is a pivot symbol.

        :param index: The index of the symbol.
        :return: True if the symbol is a pivot symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        return (
            self._symbol_status[utils.relative_index(self.stream(), index)]
            != Decoder.SymbolStatus.MISSING
        )

    def is_symbol_decoded(self, index: int) -> bool:
        """
        Check if a symbol is decoded.

        :param index: The index of the symbol.
        :return: True if the symbol is decoded.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        relative_index = utils.relative_index(self.stream(), index)
        if self._symbol_status[relative_index] != Decoder.SymbolStatus.DECODED:
            # Check coefficients
            if self.__is_coefficients_decoded(relative_index):
                self._symbol_status[relative_index] = Decoder.SymbolStatus.DECODED
                return True
            return False
        else:
            return True

    def symbol_data(self, index: int) -> bytearray:
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        return self._symbols_data[utils.relative_index(self.stream(), index)]

    def coefficients(self, index: int) -> Tuple[int, bytearray]:
        """
        Get the coefficients and coefficients offset of a symbol.

        :param index: The index of the symbol.
        :return: The coefficients offset and coefficients of a symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        relative_index = utils.relative_index(self.stream(), index)
        return (
            self._coefficients_offsets[relative_index],
            self._coefficients[relative_index],
        )

    def decode_systematic_symbol(self, symbol_data: bytearray, index: int):
        """
        Feed a systematic, i.e, un-coded symbol to the decoder.

        :param symbol_data: The data of the symbol.
        :param index: The index of the given symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index, self.stream()")

        if self.is_symbol_decoded(index):
            return

        if self.is_symbol_pivot(index):
            self.__swap_decode(symbol_data, index)

        relative_index = utils.relative_index(self.stream(), index)
        # Store the symbol
        coefficients = bytearray(1)
        self.__set_value(coefficients, index, index, 1)

        self._symbols_data[relative_index] = symbol_data
        self._coefficients[relative_index] = coefficients
        self._coefficients_offsets[relative_index] = index
        self._symbol_status[relative_index] = Decoder.SymbolStatus.DECODED

    def decode_symbol(
        self, symbol_data: bytearray, window: Range, coefficients: bytearray
    ):
        """
        Feed a coded symbol to the decoder.

        :param symbol_data: The data of the symbol.
        :param window: The window of the symbol.
        :param coefficients: The coding coefficients that describe the
                             encoding performed on the symbol.
        """
        if window.empty():
            raise ValueError("Empty window")

        if window not in self.stream():
            raise ValueError(f"Invalid window {window} for stream {self.stream()}")

        if len(window) == 1:
            self.decode_systematic_symbol(symbol_data, window.lower_bound)
            return

        pivot = self.__forward_substitute(symbol_data, window, coefficients)
        if pivot is None:
            return

        # self.__normalize(symbol_data, window, coefficients, pivot)

        # relative_pivot = utils.relative_index(self.stream(), pivot)
        # self._symbols_data[relative_pivot] = symbol_data
        # self._coefficients[relative_pivot] = coefficients
        # self._coefficients_offsets[relative_pivot] = window.lower_bound

        # self._symbol_status[relative_pivot] = Decoder.SymbolStatus.PARTIALLY_DECODED

    def __get_value(self, coefficients: bytearray, offset: int, index: int) -> int:
        """
        Get the value of a coefficient.

        :param coefficients: The coefficients.
        :param offset: The coefficients offset.
        :param index: The index of the coefficient.
        :return: The value of the coefficient.
        """
        if index < offset:
            # The index is before the start of the coeficients.
            # This may be an error, but effectively it means that the
            # coefficient is zero.
            return 0

        if index >= offset + self.field.bytes_to_elements(len(coefficients)):
            # The index is after the end of the coefficients.
            # This may be an error, but effectively it means that the
            # coefficient is zero.
            return 0

        byte_offset = (
            offset // self.field.elements_per_byte
        ) * self.field.elements_per_byte
        return self.field.get_value(coefficients, index - byte_offset)

    def __set_value(self, coefficients: bytearray, offset: int, index: int, value: int):
        """
        Get the value of a coefficient.

        :param coefficients: The coefficients.
        :param offset: The coefficients offset.
        :param index: The index of the coefficient.
        :return: The value of the coefficient.
        :param value: The value of the coefficient.
        """
        if index < offset:
            # The index is before the start of the coeficients.
            raise ValueError(f"Invalid symbol index index, before offset offset")

        if index >= offset + self.field.bytes_to_elements(len(coefficients)):
            # The index is after the end of the coefficients.
            raise ValueError(f"Invalid symbol index index, after offset offset")

        byte_offset = (
            offset // self.field.elements_per_byte
        ) * self.field.elements_per_byte
        return self.field.set_value(coefficients, index - byte_offset, value)

    def __is_coefficients_decoded(self, index: int):
        """
        Check if the coefficients at the given index are decoded.

        :param index: The index of the coefficients.
        :return: True if the coefficients are decoded, False otherwise.
        """
        if self.is_symbol_missing(index):
            return False
        elif self.is_symbol_decoded(index):
            return True

        offset, coefficients = self.coefficients(index)
        assert offset is not None
        assert coefficients is not None
        elements_count = self.field.bytes_to_elements(len(coefficients))
        for i in range(offset, offset + elements_count):
            if i == index:
                continue

            if self.__get_value(coefficients, offset, i) != 0:
                return False

        return True

    def __swap_decode(self, symbol_data: bytearray, index: int):
        """
        Swap the given symbol with an existing coded symbol.

        :param symbol_data: The data of the symbol.
        :param index: The index of the symbol.
        """
        raise NotImplementedError()

    def __forward_substitute(
        self, symbol_data: bytearray, window: Range, coefficients: bytearray
    ) -> Optional[int]:

        offset = window.upper_bound

        # Loop over all the symbol/coefficient indicies in the frame
        pivot = None
        for index in window:

            coefficient = self.__get_value(coefficients, offset, index)

            if coefficient == 0:
                # If the coefficient is zero we move to the next index
                continue

            if self.is_symbol_pivot(index):
                if pivot is None:
                    # If we have a non-zero coefficient and not already a pivot
                    # we found a pivot
                    pivot = index
                continue

            # We already have a pivot here get the corresponding symbol and
            # coefficients vector and elimitate those in the incoming symbol
            symbol_data_i = self.symbol_data(index)
            is_symbol_decoded_i = self.is_symbol_decoded(index)
            offset_i, coefficients_i = self.coefficients(index)

            """
            0 0 0 0 0 0 0 1 0 0 0 0    offset: 0
              0 0 0 0 0 0 1 0 0 0 0 0  offset: 1
                0 0 0 0 0 1 0 0 0      offset: 2
            0 0 0 0 0 0 0 1 0 0 0 0    offset: 0
                        0 1 0 0 0 0    offset: 5
            """
            if coefficient == 1:
                self.field.vector_subtract_into(
                    memoryview(coefficients)[offset:],
                    memoryview(coefficients_i)[offset_i:],
                )
                self.field.vector_subtract_into(symbol_data, symbol_data_i)
            else:
                self.field.vector_multiply_subtract_into(
                    memoryview(coefficients)[offset:],
                    memoryview(coefficients_i)[offset_i:],
                    coefficient,
                )
                self.field.vector_multiply_subtract_into(
                    symbol_data, symbol_data_i, coefficient
                )

            # If the stored symbol is larger than the one we're
            # processing - adjust the size of the incoming symbol
            if len(symbol_data_i) > len(symbol_data):
                assert not is_symbol_decoded_i
                extra = symbol_data_i[len(symbol_data) :]
                self.field.vector_multiply_into(extra, coefficient)
                symbol_data.extend(extra)

        return pivot
