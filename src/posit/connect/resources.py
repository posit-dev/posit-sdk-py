from __future__ import annotations

import posixpath
import warnings
from abc import ABC

from typing_extensions import (
    TYPE_CHECKING,
    Any,
    Hashable,
    ItemsView,
    Iterable,
    Iterator,
    List,
    Protocol,
    Sequence,
    SupportsIndex,
    TypeVar,
    cast,
    overload,
)

from .context import Context
from .paginator import Paginator

if TYPE_CHECKING:
    from .context import Context


class BaseResource(dict):
    def __init__(self, ctx: Context, /, **kwargs):
        super().__init__(**kwargs)
        self._ctx = ctx

    def __getattr__(self, name):
        if name in self:
            warnings.warn(
                f"Accessing the field '{name}' via attribute is deprecated and will be removed in v1.0.0. "
                f"Please use __getitem__ (e.g., {self.__class__.__name__.lower()}['{name}']) for field access instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return self[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Resources:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx


class Active(ABC, BaseResource):
    def __init__(self, ctx: Context, path: str, /, **attributes):
        """A dict abstraction for any HTTP endpoint that returns a singular resource.

        Extends the `Resource` class and provides additional functionality for via the session context and an optional parent resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the resource endpoint
        **attributes : dict
            Resource attributes passed
        """
        super().__init__(ctx, **attributes)
        self._ctx = ctx
        self._path = path


class Resource(Protocol):
    def __getitem__(self, key: Hashable) -> Any: ...

    def items(self) -> ItemsView: ...


class _Resource(dict, Resource):
    def __init__(self, ctx: Context, path: str, **attributes):
        self._ctx = ctx
        self._path = path
        super().__init__(**attributes)

    def destroy(self) -> None:
        self._ctx.client.delete(self._path)

    def update(self, **attributes):  # type: ignore[reportIncompatibleMethodOverride]
        response = self._ctx.client.put(self._path, json=attributes)
        result = response.json()
        super().update(**result)


_T = TypeVar("_T", bound=Resource)
_T_co = TypeVar("_T_co", bound=Resource, covariant=True)


class ResourceFactory(Protocol[_T_co]):
    def __call__(self, ctx: Context, path: str, **attributes: Any) -> _T_co: ...


class ResourceSequence(Protocol[_T]):
    @overload
    def __getitem__(self, index: SupportsIndex, /) -> _T: ...

    @overload
    def __getitem__(self, index: slice, /) -> List[_T]: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[_T]: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...


class _ResourceSequence(Sequence[_T], ResourceSequence[_T]):
    def __init__(
        self,
        ctx: Context,
        path: str,
        factory: ResourceFactory[_T_co] = _Resource,
        uid: str = "guid",
    ):
        self._ctx = ctx
        self._path = path
        self._uid = uid
        self._factory = factory

    def __getitem__(self, index):
        return list(self.fetch())[index]

    def __len__(self) -> int:
        return len(list(self.fetch()))

    def __iter__(self) -> Iterator[_T]:
        return iter(self.fetch())

    def __str__(self) -> str:
        return str(self.fetch())

    def __repr__(self) -> str:
        return repr(self.fetch())

    def create(self, **attributes: Any) -> _T:
        response = self._ctx.client.post(self._path, json=attributes)
        result = response.json()
        uid = result[self._uid]
        path = posixpath.join(self._path, uid)
        resource = self._factory(self._ctx, path, **result)
        resource = cast(_T, resource)
        return resource

    def fetch(self, **conditions: Any) -> Iterable[_T]:
        response = self._ctx.client.get(self._path, params=conditions)
        results = response.json()
        resources: List[_T] = []
        for result in results:
            uid = result[self._uid]
            path = posixpath.join(self._path, uid)
            resource = self._factory(self._ctx, path, **result)
            resource = cast(_T, resource)
            resources.append(resource)

        return resources

    def find(self, *args: str) -> _T:
        path = posixpath.join(self._path, *args)
        response = self._ctx.client.get(path)
        result = response.json()
        resource = self._factory(self._ctx, path, **result)
        resource = cast(_T, resource)
        return resource

    def find_by(self, **conditions: Any) -> _T | None:
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        **conditions : Any

        Returns
        -------
        Optional[T]
            The first record matching the conditions, or `None` if no match is found.
        """
        collection = self.fetch(**conditions)
        return next((v for v in collection if v.items() >= conditions.items()), None)


class _PaginatedResourceSequence(_ResourceSequence[_T]):
    def fetch(self, **conditions: Any) -> Iterable[_T]:
        paginator = Paginator(self._ctx, self._path, dict(**conditions))
        for page in paginator.fetch_pages():
            resources = []
            results = page.results
            for result in results:
                uid = result[self._uid]
                path = posixpath.join(self._path, uid)
                resource = self._factory(self._ctx, path, **result)
                resource = cast(_T, resource)
                resources.append(resource)
            yield from resources
