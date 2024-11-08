from packaging import version

from posit import connect

client = connect.Client()
client_version = client.version
assert client_version is not None
CONNECT_VERSION = version.parse(client_version)
