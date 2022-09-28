#! /usr/bin/env python
# encoding: utf-8

import pyerasure


def test_run():
    polynomial = 37

    table = pyerasure.full_table(polynomial)
    table.print()

    assert(False)

    pass