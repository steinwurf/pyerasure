# License for Commercial Usage
# Distributed under the "KODO EVALUATION LICENSE 1.3"
# Licensees holding a valid commercial license may use this project in
# accordance with the standard license agreement terms provided with the
# Software (see accompanying file LICENSE.rst or
# https://www.steinwurf.com/license), unless otherwise different terms and
# conditions are agreed in writing between Licensee and Steinwurf ApS in which
# case the license will be regulated by that separate written agreement.
#
# License for Non-Commercial Usage
# Distributed under the "KODO RESEARCH LICENSE 1.2"
# Licensees holding a valid research license may use this project in accordance
# with the license agreement terms provided with the Software
# See accompanying file LICENSE.rst or https://www.steinwurf.com/license

from . import online

class full_table:

    def __init__(self, p):
        """
        Precomputes and creates two lookup table for multiplying
        and dividing elements in a given 2^m binary extension field.

        p, the irreducible polynomial used
        m, the degree of the irreducible polynomial
        """

        self.degree = online.find_degree(p)

        # The number of elements in the field
        self.order = 1 << self.degree

        # Allocate the two tables
        self.multiply_table = [0]*self.order*self.order
        self.division_table = [0]*self.order*self.order

        for i in range(self.order):
            offset = i * self.order

            for j in range(self.order):
                self.multiply_table[offset+j] = online.multiply(i, j, p)

                if j == 0: # Cannot divide by zero
                    continue

                self.division_table[offset+j] = online.divide(i, j, p)

    def multiply(self, a, b):
        """
        Multiplies two binary extension field elements using the
        pre-compute lookup table.
        For each element there are 2^m results, this is used to
        index into the table

        a, the first polynomial
        b, the second polynomial
        """
        return self.multiply_table[(a << self.degree) + b]


    def divide(self, a, b):
        """
        Divides two binary extension field elements using the
        pre-compute lookup table.
        For each element there are 2^m results, this is used to
        index into the table

        a, the first polynomial
        b, the second polynomial
        """
        return self.division_table[(a << self.degree) + b]

    def print(self):
        """
        Prints the pre-computed lookup tables
        """
        print("Degree: ", self.degree)
        print("Order: ", self.order)
        online.print_polynomial(self.p)

        print("Multiply table")
        for i in range(len(self.multiply_table)):
            print(self.multiply_table[i], end=" ")
            if (i+1) % (self.order) == 0:
                print("")

        print("Division table")
        for i in range(len(self.division_table)):
            print(self.division_table[i], end=" ")
            if (i+1) % (self.order) == 0:
                print("")

