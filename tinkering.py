from posit.client import Client

client = Client()
res = client.users.get_current_user()
print(res.json())
