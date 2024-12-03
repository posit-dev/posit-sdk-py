## Posit Connect SDK

> Note: this is design-by-wishful-thinking, not how things actually work today.
> To discuss or propose changes, open a PR suggesting new language.

### Connecting

To get started, import the Connect `Client` and create a connection. You can specify the `endpoint` for your Connect server URL and your `api_key`; if not specified, they'll be pulled from the environment (`CONNECT_SERVER` and `CONNECT_API_KEY`).

It is expected that `Client()` just works from within any Posit product's environment (Workbench, Connect, etc.), either by API key and prior system configuration, or by some means of identity federation.

```python
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

```python
for st in con.content.find(app_mode="streamlit"):
    print(st.title)

my_app = con.content.get("1234-5678-90ab-cdef")
for perm in my_app.permissions:
    print(perm.role)
```

### Mapping to HTTP request methods

Entities have an `.update()` method that maps to a `PATCH` request. `.delete()` is `DELETE`.

```python
my_app.update(title="Quarterly Analysis of Team Velocity")
my_app.permissions.find_one(email="first.last@example.com").update(role="owner")
my_app.permissions.find_one(email="first.last@example.com").delete()
```

Collections have a `.create()` method that maps to `POST` to create a new entity. It may be aliased to other verbs as appropriate for the entity.

```python
my_app.permissions.add(email="my.boss@example.com", role="viewer")
```

### Field/attribute naming

The Python SDK should present the interface we wish we had, and we can evolve the REST API to match that over time. It is the adapter layer that allows us to evolve the Connect API more freely.

Naming of fields and arguments in collection and entity methods should be standardized across entity types for consistency, even if this creates a gap between our current REST API specification.

As a result, the SDK takes on the burden of smoothing over the changes in the Connect API over time. Each collection and entity class may need its own adapter methods that take the current Python SDK field names and maps to the values for the version of the Connect server being used when passing to the HTTP methods.

Entity `.to_dict()` methods likewise present the names and values in the Python interface, which may not map to the actual HTTP response body JSON. There should be some other way to access the raw response body.

### Lower-level HTTP interface

The client object has `.get`, `.post`, etc. methods that pass arguments through to the `requests` methods, accepting URL paths relative to the API root and including the necessary authorization. These are invoked inside the collection and entity action methods, and they are also available for users to call directly, whether because there are API resources we haven't wrapped in Pythonic methods yet, or because they are simpler RPC-style endpoints that just need to be hit directly.

### Constructing classes

Classes that contain dictionary-like data should inherit from `ReadOnlyDict` (or one of its subsclasses) and classes that contain list-like data should inherit from `ReadOnlySequence` (or one of its subsclasses).

#### Classes

`ReadOnlyDict` was created to provide a non-interactive interface to the data being returned for the class. This way users can not set any values without going through the API. By extension, any method that would change the data should return a new instance with the updated data. E.g. `.update()` methods should return a instance. The same applies for `ReadOnlySequence` classes.

When retrieving objects from the server, it should be retrieved through a `@property` method. This way, the data is only retrieved when it is needed. This is especially important for list-like objects.

```python
class ContentItem(..., ContentItemActiveDict):
    ...

    @property
    def repository(self) -> ContentItemRepository | None:
        try:
            return ContentItemRepository(self._ctx)
        except ClientError:
            return None

    ...
```

To avoid confusion between api exploration and internal values, all internal values should be prefixed with an underscore. This way, users can easily see what is part of the API and what is part of the internal workings of the class.

Attempt to minimize the number of locations where the same intended `path` is defined. Preferably only at `._path` (so it works with `ApiCallMixin`).

```python
class Bundles(ApiCallMixin, ContextP[ContentItemContext]):
    def __init__(
        self,
        ctx: ContentItemContext,
    ) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = f"v1/content/{ctx.content_guid}/bundles"
    ...
```

#### Context

* `Context` - A convenience class that holds information that can be passed down to child classes.
  * Contains the request  `.session` and `.url` information for easy API calls.
  * By inheriting from `Context`, it can be extended to contain more information (e.g. `ContentItemContext` adds `.content_path` and `.content_guid` to remove the requirement of passing through `content_guid` as a parameter).
  * These classes help prevent an explosion of parameters being passed through the classes.
* `ContextP` - Protocol class that defines the attributes that a Context class should have.
* `ContextT` - Type variable that defines the type of the Context class.
* `ApiCallMixin` - Mixin class that provides helper methods for API calls and parsing the JSON repsonse. (e.g. `._get_api()`)
  * It requires `._path: str` to be defined on the instance.

#### Ex: Content Item helper classes

These example classes show how the Entity and Context classes can be extended to provide helper classes for classes related to `ContentItem`.

* `ContentItemP` - Extends `ContextP` with context class set to `ContentItemContext`.
* `ContentItemContext` - Extends `Context` by including `content_path` and `content_guid` attributes.
* `ContentItemResourceDict` - Extends `ResourceDict` with context class set to `ContentItemContext`.
* `ContentItemActiveDict` - Extends `ActiveDict` with context class set to `ContentItemContext`.

#### Entity Classes

All entity classes are populated on initialization.

* `ReadOnlyDict` - A class that provides a read-only dictionary interface to the data.
  * Immutable dictionary-like object that can be iterated over.
* `ResourceDict` - Extends `ReadOnlyDict`, but is aware of `._ctx: ContextT`.
* `ActiveDict` - Extends `ResourceDict`, but is aware of the API calls (`ApiCallMixin`) that can be made on the data.

Example: `Bundle` class's init method

```python
class BundleContext(ContentItemContext):
    bundle_id: str

    def __init__(self, ctx: ContentItemContext, /, *, bundle_id: str) -> None:
        super().__init__(ctx, content_guid=ctx.content_guid)
        self.bundle_id = bundle_id

class Bundle(ApiDictEndpoint[BundleContext]):
    def __init__(self, ctx: ContentItemContext, /, **kwargs) -> None:
        bundle_id = kwargs.get("id")
        assert isinstance(bundle_id, str), f"Bundle 'id' must be a string. Got: {id}"
        assert bundle_id, "Bundle 'id' must not be an empty string."

        bundle_ctx = BundleContext(ctx, bundle_id=bundle_id)
        path = f"v1/content/{ctx.content_guid}/bundles/{bundle_id}"
        get_data = len(kwargs) == 1  # `id` is required
        super().__init__(bundle_ctx, path, get_data, **kwargs)
    ...
```

When possible `**kwargs` should be typed with `**kwargs: Unpack[_Attrs]` where `_Attrs` is a class that defines the attributes that can be passed to the class.  (Please define the attribute class within the usage class and have its name start with a `_`) By using `Unpack` and `**kwargs`, it allows for future new/conflicting parameters can be type ignored by the caller, but they will be sent through in the implementation.

Example:

```python
class Association(ResourceDict):
    class _Attrs(TypedDict, total=False):
        app_guid: str
        """The unique identifier of the content item."""
        oauth_integration_guid: str
        """The unique identifier of an existing OAuth integration."""
        oauth_integration_name: str
        """A descriptive name that identifies the OAuth integration."""
        oauth_integration_description: str
        """A brief text that describes the OAuth integration."""
        oauth_integration_template: str
        """The template used to configure this OAuth integration."""
        created_time: str
        """The timestamp (RFC3339) indicating when this association was created."""

    def __init__(self, ctx: Context, /, **kwargs: Unpack["Association._Attrs"]) -> None:
        super().__init__(ctx, **kwargs)
```

#### Collection classes

* `ReadOnlySequence` - A class that provides a read-only list interface to the data.
  * Immutable list-like object that can be iterated over.
* `ResourceSequence` - Extends `ReadOnlySequence`, but is aware of `._ctx: ContextT`.
  * Wants data to immediately exist in the class.
* `ActiveSequence` - Extends `ResourceSequence`, but is aware of the API calls that can be made on the data. It requires `._path`
  * Requires `._create_instance(path: str, **kwars: Any) -> ResourceDictT` method to be implemented.
  * During initialization, if the data is not provided, it will be fetched from the API. (...unless `get_data=False` is passed as a parameter)
* `ActiveFinderSequence` - Extends `ActiveSequence` with `.find()` and `.find_by()` methods.

For Collections classes, if no data is to be maintained, the class should inherit from `ContextP[CONTEXT_CLASS]`. This will help pass through the `._ctx` to children objects. If API calls are needed, it can also inherit from `ApiCallMixin` to get access to its conveniece methods (e.g. `._get_api()` which returns a parsed json result).


When making a new class,
* Use a class to define the parameters and their types
  * If attaching the type info class to the parent class, start with `_`. E.g.: `ContentItemRepository._Attrs`
* Document all attributes like normal
  * When the time comes that there are multiple attribute types, we can use overloads with full documentation and unpacking of type info class for each overload method.
* Inherit from `ApiDictEndpoint` or `ApiListEndpoint` as needed
  * Init signature should be `def __init__(self, ctx: Context, path: str, /, **attrs: Jsonifiable) -> None:`
