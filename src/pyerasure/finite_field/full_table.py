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

from . import online


class FullTable:
    def __init__(self, polynomial: int):
        """
        Precomputes and creates two lookup table for multiplying
        and dividing elements in a given 2ᴹ binary extension field.

        :param polynomial: The irreducible polynomial defining the field.
        """

        self.polynomial = polynomial
        self.degree = online.find_degree(polynomial)

        # The number of elements in the field
        self.order = 1 << self.degree

        # Allocate the two tables
        self.multiply_table = [0] * self.order * self.order
        self.division_table = [0] * self.order * self.order

        for i in range(self.order):
            offset = i * self.order

            for j in range(self.order):
                self.multiply_table[offset + j] = online.multiply(i, j, polynomial)

                if j == 0:  # Cannot divide by zero
                    continue

                self.division_table[offset + j] = online.divide(i, j, polynomial)

    def multiply(self, a: int, b: int) -> int:
        """
        Multiplies two binary extension field elements using the
        pre-compute lookup table.
        For each element there are 2ᴹ results, this is used to
        index into the table

        :param a: The first element to multiply.
        :param b: The second element to multiply.
        :return: The result of the multiplication.
        """

        return self.multiply_table[(a << self.degree) + b]

    def divide(self, a: int, b: int) -> int:
        """
        Divides two binary extension field elements using the
        pre-compute lookup table.
        For each element there are 2ᴹ results, this is used to
        index into the table

        :param a: The first element to divide.
        :param b: The second element to divide.
        :return: The result of the division.
        """

        return self.division_table[(a << self.degree) + b]

    def print(self):
        """
        Prints the pre-computed lookup tables
        """
        print("Degree: ", self.degree)
        print("Order: ", self.order)
        print("Polynomial: ", online.polynomial_to_string(self.polynomial))

        print("Multiply table")
        for i in range(len(self.multiply_table)):
            print(self.multiply_table[i], end=" ")
            if (i + 1) % (self.order) == 0:
                print("")

        print("Division table")
        for i in range(len(self.division_table)):
            print(self.division_table[i], end=" ")
            if (i + 1) % (self.order) == 0:
                print("")
