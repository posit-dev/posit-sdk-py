"""System Information."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from typing_extensions import TypedDict, Unpack

from .context import ContextManager
from .resources import Active

if TYPE_CHECKING:
    from posit.connect.context import Context


# from posit import connect
# from posit.connect.system import System, SystemCache

# client = connect.Client()
# system: System = client.system
# caches: List[SystemCache]: system.caches.find()
# for cache in caches:
#     task = cache.destroy(dry_run=True)


class System(ContextManager):
    """System information."""

    def __init__(self, ctx: Context, path: str) -> None:
        super().__init__()
        self._ctx: Context = ctx
        # v1/system
        self._path: str = path

    @property
    def caches(self) -> SystemCaches:
        """
        List all system caches.

        Returns
        -------
        SystemCaches
            Helper class for system caches.

        Examples
        --------
        ```python
        TODO-barret!
        # List all content runtime caches
        caches = system.caches.find()
        for cache in caches:
            task = cache.destroy(dry_run=True)
        ```

        """
        path = self._path + "/caches"
        return SystemCaches(self._ctx, path)


class SystemRuntimeCacheAttrs(TypedDict, total=False):
    language: str  # "Python"
    """The runtime language of the cache."""
    version: str  # "3.8.12"
    """The language version of the cache."""
    image_name: str  # "Local"
    """The name of the cache's execution environment."""


class SystemRuntimeCacheDestroyed(SystemRuntimeCacheAttrs, total=False):
    task_id: str
    """The identifier for the created eployment task. Always `null` for dry-run requests."""


class SystemRuntimeCache(Active):
    def __init__(
        self,
        ctx: Context,
        path: str,
        /,
        **kwargs: Unpack[SystemRuntimeCacheAttrs],
    ) -> None:
        super().__init__(ctx, path, **kwargs)

    class _DestroyAttrs(TypedDict, total=False):
        dry_run: bool
        """If `True`, the cache will not be destroyed, only the operation will be simulated."""

    def destroy(self, **kwargs: Unpack[SystemRuntimeCache._DestroyAttrs]) -> None:
        """
        Delete a content runtime package cache.

        This action is only available to administrators.

        Parameters
        ----------
        dry_run : bool, optional
            If `True`, the cache will not be destroyed, only the operation will be simulated.

        Examples
        --------
        ```python
        TODO-barret!
        # Destroy the runtime cache
        task = runtime_cache.destroy(dry_run=True)
        ```
        """
        url = self._ctx.url + self._path
        data = dict(self)
        response = self._ctx.session.delete(url, json={**data, **kwargs})
        return response.json()


class SystemCaches(ContextManager):
    """System caches."""

    def __init__(self, ctx: Context, path: str) -> None:
        super().__init__()
        self._ctx: Context = ctx
        # v1/system/caches
        self._path: str = path

    @property
    def runtime(self) -> SystemRuntimeCaches:
        """
        System runtime caches.

        Returns
        -------
        SystemRuntimeCaches
            Helper class to manage system runtime caches.

        Examples
        --------
        ```python
        TODO-barret!
        # List all content runtime caches
        caches = system.caches.find()
        for cache in caches:
            task = cache.destroy(dry_run=True)
        ```
        """
        path = self._path + "/runtime"
        return SystemRuntimeCaches(self._ctx, path)


class SystemRuntimeCaches(ContextManager):
    """
    System runtime caches.

    List all content runtime caches. These include packrat and Python
    environment caches.

    This information is available only to administrators.
    """

    def __init__(self, ctx: Context, path: str) -> None:
        super().__init__()
        self._ctx: Context = ctx
        # v1/system/caches/runtime
        self._path: str = path

    def find(self) -> List[SystemRuntimeCache]:
        """
        List all content runtime caches.

        List all content runtime caches. These include packrat and Python
        environment caches.

        This information is available only to administrators.

        Returns
        -------
        List[SystemRuntimeCache]
            List of all content runtime caches.

        Examples
        --------
        ```python
        TODO-barret!
        # List all content runtime caches
        runtime_caches = system.caches.runtime.find()
        for runtime_cache in runtime_caches:
            task = runtime_cache.destroy(dry_run=True)
        ```
        """
        url = self._ctx.url + self._path
        response = self._ctx.session.get(url)
        results = response.json()
        return [SystemRuntimeCache(**result) for result in results]

    # TODO-barret overloads
    def destroy(cache: SystemRuntimeCache | None , / , kwargs)
        TODO-barret implementations
