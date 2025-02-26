# pyright: reportFunctionMemberAccess=false
from unittest.mock import patch

import pytest

from posit.environment import (
    get_product,
    is_local,
    is_running_on_connect,
    is_running_on_workbench,
)


@pytest.mark.parametrize(
    ("posit_product", "rstudio_product", "expected"),
    [
        ("CONNECT", None, "CONNECT"),
        (None, "WORKBENCH", "WORKBENCH"),
        ("CONNECT", "WORKBENCH", "CONNECT"),
        (None, None, None),
    ],
)
def test_get_product(posit_product, rstudio_product, expected):
    env = {}
    if posit_product is not None:
        env["POSIT_PRODUCT"] = posit_product
    if rstudio_product is not None:
        env["RSTUDIO_PRODUCT"] = rstudio_product
    with patch.dict("os.environ", env, clear=True):
        assert get_product() == expected


def test_is_local():
    with patch("posit.connect.helpers.get_product", return_value=None):
        assert is_local() is True

    with patch("posit.connect.helpers.get_product", return_value="CONNECT"):
        assert is_local() is False


def test_is_running_on_connect():
    with patch("posit.connect.helpers.get_product", return_value="CONNECT"):
        assert is_running_on_connect() is True

    with patch("posit.connect.helpers.get_product", return_value="WORKBENCH"):
        assert is_running_on_connect() is False


def test_is_running_on_workbench():
    with patch("posit.connect.helpers.get_product", return_value="WORKBENCH"):
        assert is_running_on_workbench() is True

    with patch("posit.connect.helpers.get_product", return_value="CONNECT"):
        assert is_running_on_workbench() is False
