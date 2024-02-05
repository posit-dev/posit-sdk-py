from posit.connect import make_client

client = make_client()
for user in client.users.find({"username": "aaron"}):
    print(user)

print(client.users.find_one())

print(client.users.find_one({"guid": "f155520a-ca2e-4084-b0a0-12120b7d1add"}))
