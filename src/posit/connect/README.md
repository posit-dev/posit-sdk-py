## Posit Connect SDK

> Note: this is design-by-wishful-thinking, not how things actually work today.
> To discuss or propose changes, open a PR suggesting new language.
### Connecting

To get started, import the Connect `Client` and create a connection. You can specify the `endpoint` for your Connect server URL and your `api_key`; if not specified, they'll be pulled from the environment (`CONNECT_SERVER` and `CONNECT_API_KEY`).

It is expected that `Client()` just works from within any Posit product's environment (Workbench, Connect, etc.), either by API key and prior system configuration, or by some means of identity federation.

```
from posit.connect import Client

con = Client()
```

### Collections and entities

Many resources in the SDK refer to *collections* of *entities* or records in Connect.

All of the general collections can be referenced as properties of the Client object (e.g. `client.content`, `client.users`). Some collections belong to a single entity and are referenced from them similarly (e.g. `content_item.permissions`). 

All collections are iterable objects with all read-only List-like methods implemented. They also have the following methods:

* `.find()`: returns another iterable collection object. 
    * Calling `.find()` with no arguments retrieves all available entities
    * If no entities match the query, `.find()` returns a length-0 collection.
    * Iterating over a collection without having first called `find()` is equivalent to having queried for all.
    * `find()` should use query-based REST APIs where existing, and fall back to retrieving all and filtering client-side where those APIs do not (yet) exist.
    * Should `collection.find().find()` work? Probably.
* `.get(guid)` method that returns a single entity by id. If one is not found, it raises `NotFoundError`
* `.find_one()` is a convenience method that queries with `.find()` and returns a single entity
    * If more than one entity match the query, `.find_one()` returns the first
    * If no entities match, `.find_one()` returns `None`
    * If you need stricter behavior (e.g. you want to be sure that one and only one entity are returned by your query), use `.find()` or `.get()`.
* `.to_pandas()` materializes the collection in a pandas `DataFrame`. 
    * pandas is not a required dependency of the SDK. `.to_pandas()` should try to import inside the method.

The `.find()` and `.find_one()` methods use named arguments rather than accepting a dict so that IDE tab completion can work. 

Collections should handle all API reponse pagination invisibly so that the Python user doesn't need to worry about pages. 

Entities have methods that are appropriate to them. Fields in the entity bodies can be accessed as properties. 

```
for st in con.content.find(app_mode="streamlit"):
    print(st.title)

my_app = con.content.get("1234-5678-90ab-cdef")
for perm in my_app.permissions:
    print(perm.role)
```

### Mapping to HTTP request methods

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

### Field/attribute naming

The Python SDK should present the interface we wish we had, and we can evolve the REST API to match that over time. It is the adapter layer that allows us to evolve the Connect API more freely. 

Naming of fields and arguments in collection and entity methods should be standardized across entity types for consistency, even if this creates a gap between our current REST API specification. 

As a result, the SDK takes on the burden of smoothing over the changes in the Connect API over time. Each collection and entity class may need its own adapter methods that take the current Python SDK field names and maps to the values for the version of the Connect server being used when passing to the HTTP methods. 

Entity `.to_dict()` methods likewise present the names and values in the Python interface, which may not map to the actual HTTP response body JSON. There should be some other way to access the raw response body.

### Lower-level HTTP interface

The client object has `.get`, `.post`, etc. methods that pass arguments through to the `requests` methods, accepting URL paths relative to the API root and including the necessary authorization. These are invoked inside the collection and entity action methods, and they are also available for users to call directly, whether because there are API resources we haven't wrapped in Pythonic methods yet, or because they are simpler RPC-style endpoints that just need to be hit directly. 