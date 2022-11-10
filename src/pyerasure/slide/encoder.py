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
from pyerasure import finite_field
from pyerasure import utils
from ..range import Range


class Encoder:
    """The sliding window encoder class is used for encoding a continuous stream of symbols."""

    def __init__(
        self,
        field: Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8],
        max_symbol_bytes: int,
    ):
        """
        The encoder constructor.

        :param field: the chosen finite field.
        :param max_symbol_bytes: The maximum size of given symbols in bytes.
        """
        self._field = field
        self._max_symbol_bytes = max_symbol_bytes
        self._stream: Range = Range(0, 0)
        self._symbols: list[bytes] = []

    @property
    def max_symbol_bytes(self) -> int:
        """The maximum size of given symbols in bytes."""
        return self._max_symbol_bytes

    @property
    def field(
        self,
    ) -> Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8]:
        """The chosen finite field."""
        return self._field

    def push_symbol(self, symbol_data: bytes):
        """
        Push a symbol on to the encoder's FIFO stream.

        :param index: The index of the symbol.
        :param symbol_data: The data of the symbol.
        """
        if len(symbol_data) > self.max_symbol_bytes:
            raise ValueError("Symbol data is too large.")

        self._symbols.append(symbol_data)
        self.stream().push()

    def pop_symbol(self) -> bytes:
        """
        Pop a symbol from the encoder's FIFO stream.
        """
        if self.stream().empty():
            raise ValueError("Stream is empty.")

        self.stream().pop()
        return self._symbols.pop(0)

    def stream(self) -> Range:
        """
        Return the stream of symbols.
        """
        return self._stream

    def symbol_data(self, index: int) -> bytes:
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        :return: The data of the symbol.
        """
        if index not in self.stream():
            raise ValueError("Symbol not in stream.")
        return self._symbols[utils.relative_index(self.stream(), index)]

    def encode_symbol(self, window: Range, coefficients: bytes) -> bytearray:
        """
        Encode a symbol based on the given coefficients.

        :window: The window of symbols to use for encoding.
        :param coefficients: The coding coefficients that describe the
                             encoding.
        :return: The encoded symbol.
        """

        if window not in self.stream():
            raise ValueError("Window not in stream.")

        # when using a sub byte field we need to offset the coefficients
        # to the correct position in the byte
        in_byte_offset = window.lower_bound % self._field.bytes_to_elements(1)

        written = 0
        symbols = []
        for index in window:
            relative_index = utils.relative_index(window, index)
            coefficient = self.field.get_value(
                coefficients, in_byte_offset + relative_index
            )
            if coefficient == 0:
                continue

            assert index in self.stream()
            symbol_data = self.symbol_data(index)
            symbols.append((coefficient, symbol_data))
            written = max(written, len(symbol_data))

        encoded_symbol = bytearray(written)
        for coefficient, symbol_data in symbols:
            self.field.vector_multiply_add_into(
                encoded_symbol, symbol_data, coefficient
            )

        return encoded_symbol
