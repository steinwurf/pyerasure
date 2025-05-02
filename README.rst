.. image:: ./docs/images/icon.svg
   :height: 200px
   :align: center

Introduction
============

|Waf Python Tests| |Black| |Flake8| |Pip Install|

.. |Waf Python Tests| image:: https://github.com/steinwurf/pyerasure/actions/workflows/waf.yml/badge.svg
   :target: https://github.com/steinwurf/pyerasure/actions/workflows/waf.yml

.. |Flake8| image:: https://github.com/steinwurf/pyerasure/actions/workflows/flake.yml/badge.svg
    :target: https://github.com/steinwurf/pyerasure/actions/workflows/flake.yml

.. |Black| image:: https://github.com/steinwurf/pyerasure/actions/workflows/black.yml/badge.svg
      :target: https://github.com/steinwurf/pyerasure/actions/workflows/black.yml

.. |Pip Install| image:: https://github.com/steinwurf/pyerasure/actions/workflows/pip.yml/badge.svg
      :target: https://github.com/steinwurf/pyerasure/actions/workflows/pip.yml

What it is:

* A tool for learning erasure codes

License
-------

This project is licensed under the Steinwurf ApS research license. See the
`LICENSE`_ file for details.

.. _LICENSE: LICENSE.rst

Installation
------------

1. Setup your Github SSH key (see https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
2. Install the ``pyerasure`` tool using ``pip`` and ``git/ssh``::

      python3 -m pip install git+ssh://git@github.com/steinwurf/pyerasure@[TAG]

   .. note::

      The ``[TAG]`` should be replaced with the desired version or checksum
      of the tool.

3. Run the ``pyerasure`` hello world example::

      python3 examples/hello_world.py
