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


def polynomial_to_string(a):
    """Print the polynomial representation of a finite field value

    a, the polynomial to print
    """
    degree = find_degree(a)
    polynomial = ""

    for i in range(degree, -1, -1):
        if not a & (1 << i):
            continue

        if i > 1:
            polynomial = polynomial + "X^%d + " % i
        elif i == 1:
            polynomial = polynomial + "X + "
        else:
            polynomial = polynomial + "1"

    return polynomial


def find_degree(a):
    """
    Finds returns the degree of the polynomial
    i.e. the number 5 = 101 = X^2 + 1 has degree 2

    a, the polynomial whos degree we wish to find
    """
    degree = 0

    a = a >> 1

    while a > 0:
        degree = degree + 1
        a = a >> 1

    return degree


def multiply(a, b, p):
    """
    Performs the simple online multiply algorithm in the
    2^m extension field

    a, the first polynomial
    b, the second polynomial
    p, the irreducible polynomial
    """

    if a == 0 or b == 0:
        return 0

    degree = find_degree(p)

    # Mask to check if the degree is about to reach m
    mask = 1 << (degree - 1)
    highbit = 0

    # The resulting polynomial
    c = 0

    for i in range(degree):

        if b == 0:
            break

        if b & 1:
            c = c ^ a

        highbit = a & mask

        a = a << 1
        b = b >> 1

        if highbit:
            a = a ^ p

    return c


def inverse(a, p):
    """
    Finds the inverse of a polynomial a(x) in
    the 2^m extension field

    a, the polynomial whos inverse we want
    p, the irreducible polynomial
    """
    if a == 1:
        return 1

    r_large = p
    r_small = a

    y_large = 0
    y_small = 1

    j = 0

    while r_large != 1:

        j = find_degree(r_large) - find_degree(r_small)

        if j < 0:
            r_large, r_small = r_small, r_large
            y_large, y_small = y_small, y_large

            j = abs(j)

        r_large = r_large ^ (r_small << j)
        y_large = y_large ^ (y_small << j)

    return y_large


def divide(a, b, p):
    """
    Divides the two input polynomials and find the resulting
    polynomial in the 2^m extension field

    a, the numerator polynomial
    b, the denominator polynomial
    p, the prime polynomial
    m, the degree of the prime polynomial
    """
    value = inverse(b, p)
    return multiply(value, a, p)
