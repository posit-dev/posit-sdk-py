import os

from posit import connect

def test_version():
    client = connect.Client()
    assert client.version == os.environ.get("CONNECT_VERSION")
