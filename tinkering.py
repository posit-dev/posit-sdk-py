import pandas

from posit.connect import Client

with Client() as client:
    print(pandas.DataFrame(client.users.find()))
    print(pandas.DataFrame(client.content.find()))

    print(client.me.asdict())
