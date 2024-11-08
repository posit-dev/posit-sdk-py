from packaging.version import parse

from posit import connect

client = connect.Client()
version = client.version
assert version
CONNECT_VERSION = parse(version)
