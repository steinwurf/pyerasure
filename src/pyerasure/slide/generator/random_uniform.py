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
import random
from pyerasure import finite_field
from ...range import Range
from ... import utils


class RandomUniform:
    """
    Uniform random sliding window cofficients generator.
    """

    def __init__(
        self,
        field: Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8],
    ):
        """
        The generator constructor.

        :param field: The chosen finite field.
        """
        self._field = field
        self.random = random.Random()

    @property
    def field(
        self,
    ) -> Union[finite_field.Binary, finite_field.Binary4, finite_field.Binary8]:
        """The chosen finite field."""
        return self._field

    def set_seed(self, seed: int):
        """
        Set the state of the coefficient generator. The coefficient generator
        will always produce the same set of coefficients for a given seed.

        :param seed: The seed that will set the state of the generator.
        """
        self.random.seed(seed)

    def coefficients_bytes(self, window: Range) -> int:
        """
        The number of bytes needed to store the coefficients.

        :param window: The window.
        """
        return utils.coefficients_bytes(self.field.elements_per_byte, window)

    def generate(self, window: Range) -> bytes:
        """
        Generate the coefficients.

        :param window: The window.
        """
        if window.empty():
            return b""

        coefficients = bytearray(
            self.random.getrandbits(8) for _ in range(self.coefficients_bytes(window))
        )

        frame = utils.to_frame(self.field.elements_per_byte, window)

        for i in frame:
            if i not in window:
                self.field.set_value(coefficients, utils.relative_index(frame, i), 0)

        return bytes(coefficients)
