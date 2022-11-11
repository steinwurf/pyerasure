#!/usr/bin/env python
# encoding: utf-8

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

import unittest
import pyerasure.utils
from pyerasure.range import Range


class TestUtils(unittest.TestCase):
    def test_to_frame(self):
        self.assertEqual(Range(0, 0), pyerasure.utils.to_frame(1, Range(0, 0)))
        self.assertEqual(Range(0, 0), pyerasure.utils.to_frame(2, Range(0, 0)))
        self.assertEqual(Range(0, 0), pyerasure.utils.to_frame(8, Range(0, 0)))

        self.assertEqual(Range(1, 1), pyerasure.utils.to_frame(1, Range(1, 1)))
        self.assertEqual(Range(1, 1), pyerasure.utils.to_frame(2, Range(1, 1)))
        self.assertEqual(Range(1, 1), pyerasure.utils.to_frame(8, Range(1, 1)))

        self.assertEqual(Range(0, 1), pyerasure.utils.to_frame(1, Range(0, 1)))
        self.assertEqual(Range(0, 2), pyerasure.utils.to_frame(2, Range(0, 1)))
        self.assertEqual(Range(0, 8), pyerasure.utils.to_frame(8, Range(0, 1)))

        self.assertEqual(Range(1, 2), pyerasure.utils.to_frame(1, Range(1, 2)))
        self.assertEqual(Range(0, 2), pyerasure.utils.to_frame(2, Range(1, 2)))
        self.assertEqual(Range(0, 8), pyerasure.utils.to_frame(8, Range(1, 2)))


if __name__ == "__main__":
    unittest.main()
