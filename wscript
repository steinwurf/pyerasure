#! /usr/bin/env python
# encoding: utf-8

import os
import waflib

from waflib.Build import BuildContext


VERSION = "1.0.1"


class UploadContext(BuildContext):
    cmd = "upload"
    fun = "upload"


def options(opt):

    opt.add_option(
        "--run_tests", default=False, action="store_true", help="Run all unit tests"
    )

    opt.add_option(
        "--pytest_basetemp",
        default="pytest_temp",
        help="Set the prefix folder where pytest executes the tests",
    )


def configure(conf):
    pass


def build(bld):

    # Create a virtualenv in the source folder and build universal wheel
    # Make sure the virtualenv Python module is in path
    with bld.create_virtualenv() as venv:
        venv.run(cmd="python -m pip install wheel")
        venv.run(cmd="python setup.py bdist_wheel --universal", cwd=bld.path)

        # Run the unit-tests
        if bld.options.run_tests:
            _pytest(bld=bld, venv=venv)

    # Delete the egg-info directory, do not understand why this is created
    # when we build a wheel. But, it is - perhaps in the future there will
    # be some way to disable its creation.
    egg_info = os.path.join("src", "pyerasure.egg-info")

    if os.path.isdir(egg_info):
        waflib.extras.wurf.directory.remove_directory(path=egg_info)


class ReleaseContext(BuildContext):
    cmd = "prepare_release"
    fun = "prepare_release"


def prepare_release(ctx):
    """Prepare a release."""

    # Rewrite versions
    with ctx.rewrite_file(filename="src/pyerasure/_version.py") as f:

        pattern = r'__version__ = "\d+\.\d+\.\d+"'
        replacement = '__version__ = "{}"'.format(VERSION)

        f.regex_replace(pattern=pattern, replacement=replacement)


def _find_wheel(ctx):
    """Find the .whl file in the dist folder."""

    wheel = ctx.path.ant_glob("dist/*-" + VERSION + "-*.whl")

    if not len(wheel) == 1:
        ctx.fatal("No wheel found (or version mismatch)")
    else:
        wheel = wheel[0]
        waflib.Logs.info("Wheel %s", wheel)
        return wheel


def upload(bld):
    """Upload the built wheel to PyPI (the Python Package Index)"""

    with bld.create_virtualenv() as venv:
        venv.run("python -m pip install twine")

        wheel = _find_wheel(ctx=bld)

        venv.run(f"python -m twine upload {wheel}")


def _pytest(bld, venv):

    # To update the requirements.txt just delete it - a fresh one
    # will be generated from test/requirements.in
    if not os.path.isfile("test/requirements.txt"):
        venv.run("python -m pip install pip-tools")
        venv.run(
            "pip-compile setup.py test/requirements.in "
            "--output-file test/requirements.txt"
        )

    venv.run("python -m pip install -r test/requirements.txt")

    # Install our python wheel in the virtualenv for testing
    wheel = _find_wheel(ctx=bld)

    venv.run(f"python -m pip install {wheel}")

    # We override the pytest temp folder with the basetemp option,
    # so the test folders will be available at the specified location
    # on all platforms. The default location is the "pytest" local folder.
    basetemp = os.path.abspath(os.path.expanduser(bld.options.pytest_basetemp))

    # We need to manually remove the previously created basetemp folder,
    # because pytest uses os.listdir in the removal process, and that fails
    # if there are any broken symlinks in that folder.
    if os.path.exists(basetemp):
        waflib.extras.wurf.directory.remove_directory(path=basetemp)

    # Run all tests by just passing the test directory. Specific tests can
    # be enabled by specifying the full path e.g.:
    #
    #     'test/test_run.py::test_create_context'
    #
    test_filter = "test"

    # Main test command
    venv.run(f"python -B -m pytest {test_filter} --basetemp {basetemp}")

    # Check the package
    venv.run(f"python -m pip install twine==1.15.0")
    venv.run(f"twine check {wheel}")


def docs(ctx):
    """Build the documentation in a virtualenv"""

    with ctx.create_virtualenv() as venv:

        # To update the requirements.txt just delete it - a fresh one
        # will be generated from test/requirements.in
        if not os.path.isfile("docs/requirements.txt"):
            venv.run("python -m pip install pip-tools")
            venv.run("pip-compile docs/requirements.in")

        venv.run("python -m pip install -r docs/requirements.txt")

        build_path = os.path.join(ctx.path.abspath(), "build", "docs")

        venv.run(
            "giit clean . --build_path {}".format(build_path), cwd=ctx.path.abspath()
        )

        arguments = []
        arguments.append("--build_path {}".format(build_path))
        venv.run("giit sphinx . {}".format(" ".join(arguments)), cwd=ctx.path.abspath())
