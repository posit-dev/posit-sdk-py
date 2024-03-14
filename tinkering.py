from posit.connect import Client

with Client() as client:
    user = client.users.get("f55ca95d-ce52-43ed-b31b-48dc4a07fe13")
    print(user.locked)
    print(user.is_locked)

    users = client.users.find()

    # This method of conversion provides forward compatibility against the API as fields are removed. This would require
    import pandas

    users = (user.asdict() for user in users)
    print(pandas.DataFrame(users))
