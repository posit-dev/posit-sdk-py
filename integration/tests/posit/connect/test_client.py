import os
import pytest

from posit import connect


@pytest.mark.skipif(
    os.environ.get("CONNECT_VERSION") is None,
    reason="requires CONNECT_VERSION environment variable",
)
def test_version():
    client = connect.Client()
    assert client.version == os.environ.get("CONNECT_VERSION")
