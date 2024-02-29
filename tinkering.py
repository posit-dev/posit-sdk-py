from posit.connect import Client

with Client() as client:
    # Calls the API to get the total number of users from the server.
    print(len(client.users))
    # Iterates over the users in the API and counts the length client side.
    print(len(client.users.find()))
    # Iterates over the users in the API and finds the first results that match the condition.
    print(client.users.find_one(lambda user: user["last_name"] == "Steinberg"))
