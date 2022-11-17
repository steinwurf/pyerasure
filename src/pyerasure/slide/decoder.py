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

        self._symbol_status: list[Decoder.SymbolStatus] = []
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

    def __is_symbol_decoded(self, index: int) -> bool:
        """
        Check if a symbol is decoded.

        :param index: The index of the symbol.
        :return: True if the symbol is decoded.
        """

        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        relative_index = utils.relative_index(self.stream(), index)
        return (
            self._symbol_status[utils.relative_index(self.stream(), index)]
            == Decoder.SymbolStatus.DECODED
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
        if (
            self._symbol_status[relative_index]
            == Decoder.SymbolStatus.PARTIALLY_DECODED
        ):
            # Check coefficients
            if self.__is_coefficients_decoded(index):
                self.__set_symbol_decoded(index)

        return self.__is_symbol_decoded(index)

    def __set_symbol_partial_decoded(
        self, coefficients: bytearray, window: Range, index: int
    ):
        """
        Set a symbol as partially decoded.

        :param coefficients: The coefficients of the symbol.
        :param offset: The offset of the coefficients.
        :param index: The index of the symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        relative_index = utils.relative_index(self.stream(), index)
        assert self._symbol_status[relative_index] == Decoder.SymbolStatus.MISSING

        if utils.is_coefficients_decoded(self.field, window, coefficients, index):
            self._symbol_status[relative_index] = Decoder.SymbolStatus.DECODED
            return
        self._coefficients[relative_index] = coefficients
        frame = utils.to_frame(self.field.elements_per_byte, window)
        self._coefficients_offsets[relative_index] = frame.lower_bound
        self._symbol_status[relative_index] = Decoder.SymbolStatus.PARTIALLY_DECODED

    def __set_symbol_decoded(self, index: int):
        """
        Set a symbol as decoded.

        :param index: The index of the symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        relative_index = utils.relative_index(self.stream(), index)

        assert self._symbol_status[relative_index] != Decoder.SymbolStatus.DECODED

        if (
            self._symbol_status[relative_index]
            == Decoder.SymbolStatus.PARTIALLY_DECODED
        ):
            self._coefficients[relative_index] = None
            self._coefficients_offsets[relative_index] = None

        self._symbol_status[relative_index] = Decoder.SymbolStatus.DECODED

    def symbol_data(self, index: int) -> bytearray:
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        return self._symbols_data[utils.relative_index(self.stream(), index)]

    def __set_symbol_data(self, index: int, symbol_data: bytearray):
        """
        Set the data of a symbol.

        :param index: The index of the symbol.
        :param symbol_data: The data of the symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        self._symbols_data[utils.relative_index(self.stream(), index)] = symbol_data

    def coefficients(self, index: int) -> Tuple[int, bytearray]:
        """
        Get the coefficients and coefficients offset of a symbol.

        :param index: The index of the symbol.
        :return: The coefficients offset and coefficients of a symbol.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index")

        # The coefficients are only stored for coded symbols
        assert not self.__is_symbol_decoded(index)

        relative_index = utils.relative_index(self.stream(), index)
        return (
            self._coefficients_offsets[relative_index],
            self._coefficients[relative_index],
        )

    def decode_systematic_symbol(self, symbol_data: bytearray, index: int) -> bool:
        """
        Feed a systematic, i.e, un-coded symbol to the decoder.

        :param symbol_data: The data of the symbol.
        :param index: The index of the given symbol.
        :return: True if the symbol linearly independent.
        """
        if index not in self.stream():
            raise ValueError(f"Invalid symbol index index, self.stream()")

        if self.is_symbol_decoded(index):
            return False

        if self.is_symbol_pivot(index):
            self.__swap_decode(symbol_data, index)

        # Store the symbol
        self.__set_symbol_data(index, symbol_data)
        self.__set_symbol_decoded(index)
        return True

    def decode_symbol(
        self, symbol_data: bytearray, window: Range, coefficients: bytearray
    ) -> bool:
        """
        Feed a coded symbol to the decoder.

        :param symbol_data: The data of the symbol.
        :param window: The window of the symbol.
        :param coefficients: The coding coefficients that describe the
                             encoding performed on the symbol.
        :return: True if the symbol linearly independent.
        """
        if window.empty():
            raise ValueError("Empty window")

        if window not in self.stream():
            raise ValueError(f"Invalid window {window} for stream {self.stream()}")

        if len(window) == 1:
            return self.decode_systematic_symbol(symbol_data, window.lower_bound)

        pivot = self.__forward_substitute(symbol_data, window, coefficients)
        if pivot is None:
            return False

        self.__normalize(symbol_data, window, coefficients, pivot)
        self.__set_symbol_data(pivot, symbol_data)
        self.__set_symbol_partial_decoded(coefficients, window, pivot)

        self.__backward_substitute(pivot)
        return True

    def __is_coefficients_decoded(self, index: int):
        """
        Check if the coefficients at the given index are decoded.

        :param index: The index of the coefficients.
        :return: True if the coefficients are decoded, False otherwise.
        """
        if self.is_symbol_missing(index):
            return False

        if self.__is_symbol_decoded(index):
            return True

        offset, coefficients = self.coefficients(index)
        assert offset is not None
        assert coefficients is not None
        window = Range(offset, offset + self.field.bytes_to_elements(len(coefficients)))
        return utils.is_coefficients_decoded(self.field, window, coefficients, index)

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

        pivot = None

        # Loop over all the symbol/coefficient indicies in the frame
        frame = utils.to_frame(self.field.elements_per_byte, window)
        for index in frame:
            if index not in window:
                continue

            coefficient = self.field.get_value(
                coefficients, utils.relative_index(frame, index)
            )

            if coefficient == 0:
                # If the coefficient is zero we move to the next index
                continue

            if not self.is_symbol_pivot(index):
                if pivot is None:
                    # If we have a non-zero coefficient and not already a pivot
                    # we found a pivot
                    pivot = index
                continue

            # We already have a pivot here get the corresponding symbol and
            # coefficients vector and elimitate those in the incoming symbol
            symbol_data_i = memoryview(self.symbol_data(index)).toreadonly()

            if self.is_symbol_decoded(index):
                # If symbol i is decoded, the incoming symbol
                # cannot be smaller and still contain symbol i.
                if len(symbol_data_i) > len(symbol_data):
                    symbol_data_i = symbol_data_i[: len(symbol_data)]
                    self.__set_symbol_data(index, symbol_data_i)
                assert len(symbol_data_i) <= len(symbol_data)

                self.field.vector_multiply_subtract_into(
                    symbol_data, symbol_data_i, coefficient
                )

                self.field.set_value(
                    coefficients, utils.relative_index(frame, index), 0
                )
            else:

                self.field.vector_multiply_subtract_into(
                    symbol_data,
                    # Cap the length of symbol i to the length of the incoming symbol
                    memoryview(symbol_data_i)[: len(symbol_data)],
                    coefficient,
                )

                # If the stored symbol is larger than the one we're
                # processing - adjust the size of the incoming symbol
                if len(symbol_data_i) > len(symbol_data):
                    extra = symbol_data_i[len(symbol_data) :]
                    self.field.vector_multiply_into(extra, coefficient)
                    symbol_data.extend(extra)

                offset_i, coefficients_i = self.coefficients(index)
                assert offset_i is not None
                assert coefficients_i is not None
                frame_i = utils.to_frame(
                    self.field.elements_per_byte,
                    Range(
                        offset_i,
                        offset_i + self.field.bytes_to_elements(len(coefficients_i)),
                    ),
                )

                if frame_i in frame:
                    # The coefficients_i are fully contained in the frame
                    # of coefficients
                    diff = frame.lower_bound - frame_i.lower_bound
                    self.field.vector_multiply_subtract_into(
                        memoryview(coefficients)[diff : len(coefficients) - diff],
                        memoryview(coefficients_i)[diff : len(coefficients_i) - diff],
                        coefficient,
                    )
                else:
                    # The coefficients_i are not fully contained in the frame
                    # of coefficients
                    frame_int = frame.intersect(frame_i)
                    assert not frame_int.empty()

                    self.field.vector_multiply_subtract_into(
                        memoryview(coefficients)[
                            frame_int.lower_bound
                            - frame.lower_bound : len(coefficients)
                            - (frame.upper_bound - frame_int.upper_bound)
                        ],
                        memoryview(coefficients_i)[
                            frame_int.lower_bound
                            - frame_i.lower_bound : len(coefficients_i)
                            - (frame_i.upper_bound - frame_int.upper_bound)
                        ],
                        coefficient,
                    )
                    if frame.lower_bound > frame_i.lower_bound:
                        # Handle the coefficients to the left of the frame
                        diff = frame.lower_bound - frame_i.lower_bound
                        frame.lower_bound = frame_i.lower_bound
                        window.lower_bound = frame.lower_bound
                        extra = coefficients_i[:diff]
                        self.field.vector_multiply_into(extra, coefficient)
                        # prepend extra to coefficients
                        coefficients = bytearray(extra) + coefficients

                    if frame.upper_bound < frame_i.upper_bound:
                        # Handle the coefficients to the right of the frame
                        diff = frame_i.upper_bound - frame.upper_bound
                        frame.upper_bound = frame_i.upper_bound
                        extra = coefficients_i[-diff:]
                        self.field.vector_multiply_into(extra, coefficient)
                        # append extra to coefficients
                        coefficients.extend(extra)
                    assert frame_i in frame

        return pivot

    def __backward_substitute(self, pivot: int):
        """
        Backward substitute the given pivot.

        :param pivot: The pivot to backward substitute.
        """
        symbol_data = memoryview(self.symbol_data(pivot)).toreadonly()
        is_decoded = self.is_symbol_decoded(pivot)
        offset, coefficients = self.coefficients(pivot)
        frame = utils.to_frame(
            self.field.elements_per_byte,
            Range(offset, offset + self.field.bytes_to_elements(len(coefficients))),
        )

        # We found a "1" that nobody else had as pivot, we now
        # substract this packet from other coded packets
        # - if they have non "0" on our pivot place
        for index in Range(self.stream().lower_bound, pivot):
            if self.is_symbol_missing(index):
                # We do not have a symbol yet here
                continue

            if self.is_symbol_decoded(index):
                # We know that we have no non-zero elements
                # outside the pivot position when a symbol is fully decoded
                continue

            offset_i, coefficients_i = self.coefficients(index)
            frame_i = utils.to_frame(
                self.field.elements_per_byte,
                Range(
                    offset_i,
                    offset_i + self.field.bytes_to_elements(len(coefficients_i)),
                ),
            )
            if frame_i.upper_bound <= frame.lower_bound:
                # The coefficients_i are fully to the left of the coefficients
                continue

            coefficient = self.field.get_value(
                coefficients_i, utils.relative_index(frame_i, pivot)
            )

            if coefficient == 0:
                # The coefficient is zero, skip
                continue

            symbol_data_i = self.symbol_data(index)

            if is_decoded:
                # If the incoming symbol is decoded, symbol i cannot be
                # larger than the incoming symbol
                if len(symbol_data) > len(symbol_data_i):
                    # Resize symbol i to the size of the incoming symbol
                    symbol_data_i = symbol_data_i[: len(symbol_data)]
                    self.__set_symbol_data(index, symbol_data_i)
                assert len(symbol_data) <= len(symbol_data_i)

                self.field.vector_multiply_subtract_into(
                    symbol_data_i, symbol_data, coefficient
                )
                # Zero out the coefficient at the index position
                self.field.set_value(
                    coefficients, utils.relative_index(frame, index), 0
                )
            else:
                raise NotImplementedError()
                self.field.vector_multiply_subtract_into(
                    memoryview(coefficients_i)[offset_i:],
                    memoryview(coefficients)[offset:],
                    coefficient,
                )

                self.field.vector_multiply_subtract_into(
                    symbol_data, symbol_data_i, coefficient
                )

                # If the stored symbol is larger than the one we're
                # processing - adjust the size of the incoming symbol
                if len(symbol_data_i) > len(symbol_data):
                    extra = symbol_data_i[len(symbol_data) :]
                    self.field.vector_multiply_into(extra, coefficient)
                    symbol_data.extend(extra)

            if len(symbol_data_i) < len(symbol_data):

                if is_decoded:
                    # symbol i is smaller than the incoming symbol. In this
                    # case we deduce that the incoming symbol is infact smaller
                    # than what we think it is.
                    # This is because, since the incoming symbol is decoded,
                    # and symbol_i mixed with the incoming symbol, the incoming
                    # symbol must be equal to or less than the size of symbol i.
                    symbol_data = symbol_data[: len(symbol_data_i)]
                    self.__set_symbol_data(pivot, symbol_data)
                else:
                    # Increase the number of bytes in symbol i. This
                    # happens when pivot symbol is substracted from symbol i.
                    pass

    def __normalize(
        self, symbol_data: bytearray, window: Range, coefficients: bytearray, pivot: int
    ):
        """
        Normalize the symbol.

        :param symbol_data: The data of the symbol.
        :param window: The window of the symbol.
        :param coefficients: The coefficients of the symbol.
        :param pivot: The pivot of the symbol.
        """
        frame = utils.to_frame(self.field.elements_per_byte, window)
        pivot_coefficient = self.field.get_value(
            coefficients, utils.relative_index(frame, pivot)
        )

        if pivot_coefficient == 1:
            return

        self.field.vector_multiply_into(symbol_data, pivot_coefficient)
        self.field.vector_multiply_into(coefficients, pivot_coefficient)
