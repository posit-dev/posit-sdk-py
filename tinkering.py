from posit.connect.client import create_client

with create_client() as client:
<<<<<<< HEAD
    print(client.users.get("f55ca95d-ce52-43ed-b31b-48dc4a07fe13"))

    users = client.users
    users = users.find(lambda user: user["first_name"].startswith("T"))
    users = users.find(lambda user: user["last_name"].startswith("S"))
    user = users.find_one(lambda user: user["user_role"] == "administrator")
    print(user)
=======
    users = client.users
    print(
        users.find({"username": "taylor_steinberg"}).find(
            {"username": "taylor_steinberg"}
        )
    )
    print(users.find_one({"username": "taylor_steinberg"}))
    print(users.get("f55ca95d-ce52-43ed-b31b-48dc4a07fe13"))
    print(users.to_pandas_data_frame())
>>>>>>> b5d8a18 (feat: adds users implementation with lazy server-side fetching)
