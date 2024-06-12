from posit import connect


def test_version():
    client = connect.Client()
    assert client.version
