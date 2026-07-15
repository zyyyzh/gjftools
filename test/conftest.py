import os
import pathlib
import pytest

from gjftools import gjfdata


def pytest_configure():
    base_dir = pathlib.Path(__file__).parent
    pytest.EXAMPLE_PATH = str(base_dir.joinpath("example"))
    pytest.TMP_PATH = str(pytest.EXAMPLE_PATH.joinpath("tmp"))
    # TODO: create tmp if not exist
    # TODO: clear tmp if exist

