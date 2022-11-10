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


class Encoder:
    """The block encoder class is used to encode a set of symbols."""

    def __init__(
        self,
        field: Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8],
        symbols: int,
        symbol_bytes: int,
    ):
        """
        The block encoder constructor.

        :param field: the chosen finite field.
        :param symbols: The number of symbols in the block.
        :param symbol_bytes: The size of a symbol in bytes.
        """
        self._field = field
        self._symbols = symbols
        self._symbol_bytes = symbol_bytes
        self._rank = 0
        self._symbols_data = [None] * symbols

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
        return self.symbols * self.symbol_bytes

    @property
    def rank(self) -> int:
        """The rank of the encoding matrix, i.e., the number of symbols."""
        return self._rank

    def set_symbol(self, index: int, symbol_data: bytes):
        """
        Set a symbol.

        :param index: The index of the symbol.
        :param symbol_data: The data of the symbol.
        """
        if len(symbol_data) != self.symbol_bytes:
            raise ValueError(f"Invalid symbol size {len(symbol_data)}.")
        if index >= self.symbols:
            raise ValueError(f"Invalid symbol index. {index}")
        if index != self.rank:
            raise ValueError("Symbols must be set in order.")
        self._symbols_data[index] = symbol_data
        self._rank += 1

    def set_symbols(self, block_data: bytes):
        """
        Set all symbols.

        :param block_data: The data of the block.
        """
        if len(block_data) != self.block_bytes:
            raise ValueError(f"Invalid block size {block_data}.")
        for index in range(self.symbols):
            offset = index * self.symbol_bytes
            self.set_symbol(
                index,
                block_data[offset : offset + self.symbol_bytes],
            )

    def is_symbol_set(self, index: int) -> bool:
        """
        Check if a symbol is set.

        :param index: The index of the symbol.
        :return: True if the symbol set.
        """
        if index >= self.symbols:
            raise ValueError("Invalid symbol index.")
        return self._symbols_data[index] is not None

    def symbol_data(self, index: int) -> bytes:
        """
        Get the data of a symbol.

        :param index: The index of the symbol.
        :return: The data of the symbol.
        """
        if index >= self.symbols:
            raise ValueError("Invalid symbol index.")
        return self._symbols_data[index]

    def encode_symbol(self, coefficients: bytes) -> bytearray:
        """
        Encode a symbol based on the given coefficients.

        :param coefficients: The coding coefficients that describe the
                             encoding.
        :return: The encoded symbol.
        """
        encoded_symbol = bytearray(self.symbol_bytes)
        for index in range(self.rank):
            coefficient = self.field.get_value(coefficients, index)
            if coefficient == 0:
                continue

            if not self.is_symbol_set(index):
                raise ValueError(f"Symbol not set: {index}")

            self.field.vector_multiply_add_into(
                encoded_symbol, self.symbol_data(index), coefficient
            )

        return encoded_symbol
