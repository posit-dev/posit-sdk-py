from packaging import version

from posit import connect

client = connect.Client()
CONNECT_VERSION = version.parse(client.version)
