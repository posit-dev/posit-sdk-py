## Posit Connect SDK

> Note: this is design-by-wishful-thinking, not how things actually work today.

To get started, import the Connect `Client` and create a connection. You can specify the `endpoint` for your Connect server URL and your `api_key`; if not specified, they'll be pulled from the environment (`CONNECT_SERVER` and `CONNECT_API_KEY`).

```
from posit.connect import Client

con = Client()
```

All of the general collections of entities can be referenced as properties of the Client object. Some collections belong to a single entity and are referenced from them similarly. 

All collections have a `.find()` method that returns an iterable List-like object, and a `.get(guid)` method that returns a single entity by id.

Entities have methods that are appropriate to them. Fields in the entity bodies can be accessed as properties. 

```
for st in con.content.find({"app_mode": "streamlit"}):
    print(st.title)

my_app = con.content.find_one(guid="1234-5678-90ab-cdef")
for perm in my_app.permissions.find():
    print(perm.role)
```

Entities have an `.update()` method that maps to a `PATCH` request. `.delete()` is `DELETE`. 

```
my_app.update({"title": "Quarterly Analysis of Team Velocity"})
my_app.permissions.find_one(email="first.last@example.com").update({"role": "owner"})
my_app.permissions.find_one(email="first.last@example.com").delete()
```

Collections have a `.create()` method that maps to `POST` to create a new entity. It may be aliased to other verbs as appropriate for the entity.

```
my_app.permissions.add("my.boss@example.com", "viewer")
```