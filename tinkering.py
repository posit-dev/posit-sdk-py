from posit.connect.client import create_client

with create_client() as client:
    print(client.me)
    print(client.users.get("f55ca95d-ce52-43ed-b31b-48dc4a07fe13"))
    users = client.users
    users = users.find(lambda user: user["first_name"].startswith("T"))
    users = users.find(lambda user: user["last_name"].startswith("S"))
    user = users.find_one(lambda user: user["user_role"] == "administrator")
    print(user)
