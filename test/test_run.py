#! /usr/bin/env python
# encoding: utf-8

import pyerasure


def test_run():
    table = pyerasure.full_table(37)
    table.print()

    assert(False)

    pass