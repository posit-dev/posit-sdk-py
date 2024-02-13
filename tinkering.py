from posit.connect.client import create_client

with create_client() as client:
    users = client.users
    print(
        users.find({"username": "taylor_steinberg"}).find(
            {"username": "taylor_steinberg"}
        )
    )
    print(users.find_one({"username": "taylor_steinberg"}))
    print(users.get("f55ca95d-ce52-43ed-b31b-48dc4a07fe13"))
    print(users.to_pandas_data_frame())
