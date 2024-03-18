from posit.connect import Client

with Client() as client:
    client.get("v1/users")
    client.users.get("f55ca95d-ce52-43ed-b31b-48dc4a07fe13")
    client.users.find(lambda user: user.first_name.startswith("T"))
    client.users.find_one(lambda user: user.first_name.startswith("T"))
