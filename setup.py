#! /usr/bin/env python
# encoding: utf-8

import os
import io
import re
import sys

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, "README.rst"), encoding="utf-8") as fd:
    long_description = fd.read()


def file_find_version(filepath):

    with io.open(filepath, encoding="utf-8") as fd:

        VERSION = None

        regex = re.compile(
            r"""
        (                # Group and match
            VERSION      #    Match 'VERSION'
            \s*          #    Match zero or more spaces
            =            #    Match and equal sign
            \s*          #    Match zero or more spaces
        )                # End group
        "                # Match a double quote
        (                # Group and match
            \d\.\d\.\d   #    Match digit.digit.digit e.g. 1.2.3
        )                # End of group
        "                # Match a double quote
        """,
            re.VERBOSE,
        )

        for line in fd:

            match = regex.match(line)
            if not match:
                continue

            # The second parenthesized subgroup.
            VERSION = match.group(2)
            break

        else:
            sys.exit("No VERSION variable defined in {} - aborting!".format(filepath))

    return VERSION


def find_version():

    wscript_VERSION = file_find_version(filepath=os.path.join(cwd, "wscript"))

    return wscript_VERSION


VERSION = find_version()

setup(
    name="pyerasure",
    version=VERSION,
    description=("A tool for learning erasure codes"),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/steinwurf/",
    author="Steinwurf ApS",
    author_email="contact@steinwurf.com",
    license="PyErasure Research License 1.2 / Evaluation License 1.3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications",
        "Topic :: Education",
    ],
    keywords=(
        "pyerasure",
        "erasure",
        "coding",
        "reed-solomon",
        "rlnc",
        "network coding",
    ),
    packages=find_packages(where="src", exclude=["test"]),
    package_dir={"": "src"},
    install_requires=[""],
)
