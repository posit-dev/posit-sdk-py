## Posit Connect SDK

> Note: this is design-by-wishful-thinking, not how things actually work today.

To get started, import the Connect `Client` and create a connection. You can specify the `endpoint` for your Connect server URL and your `api_key`; if not specified, they'll be pulled from the environment (`CONNECT_SERVER` and `CONNECT_API_KEY`).

It is expected that `Client()` just works from within any Posit product's environment (Workbench, Connect, etc.), either by API key and prior system configuration, or by some means of identity federation.

```
from posit.connect import Client

con = Client()
```

All of the general collections of entities can be referenced as properties of the Client object. Some collections belong to a single entity and are referenced from them similarly. 

All collections are iterable objects with all read-only List-like methods implemented.
Collections have a `.find()` method that returns another iterable collection object, and a `.get(guid)` method that returns a single entity by id.
Calling `.find()` with no arguments retrieves all available entities, and iterating over a collection without having first called `find()` is equivalent to having queried for all.
Collections should handle all API reponse pagination invisibly so that the Python user doesn't need to worry about pages. 
The `find()` method should use named arguments rather than accepting a dict so that IDE tab completion can work. 

Naming of fields/arguments in collection and entity methods should be standardized across entity types for consistency, even if this creates a gap between our current REST API specification. The Python SDK should present the interface we wish we had, and we can evolve the REST API to match that over time.

`find()` should use query-based REST APIs where existing, and fall back to retrieving all and filtering client-side where those APIs do not (yet) exist.

Entities have methods that are appropriate to them. Fields in the entity bodies can be accessed as properties. 

```
for st in con.content.find(app_mode="streamlit"):
    print(st.title)

my_app = con.content.get("1234-5678-90ab-cdef")
for perm in my_app.permissions:
    print(perm.role)
```

Entities have an `.update()` method that maps to a `PATCH` request. `.delete()` is `DELETE`. 

```
my_app.update(title="Quarterly Analysis of Team Velocity")
my_app.permissions.find_one(email="first.last@example.com").update(role="owner")
my_app.permissions.find_one(email="first.last@example.com").delete()
```

Collections have a `.create()` method that maps to `POST` to create a new entity. It may be aliased to other verbs as appropriate for the entity.

```
my_app.permissions.add(email="my.boss@example.com", role="viewer")
```