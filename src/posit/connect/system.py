"""System Information."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, overload

from typing_extensions import TypedDict, Unpack

from .context import ContextManager
from .resources import Active

if TYPE_CHECKING:
    from posit.connect.context import Context

    from .tasks import Task


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
        from posit.connect import Client

        client = Client()

        caches = client.system.caches.runtime.find()
        ```

        """
        path = self._path + "/caches"
        return SystemCaches(self._ctx, path)


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
        from posit.connect import Client

        client = Client()

        caches = client.system.caches.runtime.find()
        ```
        """
        path = self._path + "/runtime"
        return SystemRuntimeCaches(self._ctx, path)


class SystemRuntimeCache(Active):
    class _Attrs(TypedDict, total=False):
        language: str  # "Python"
        """The runtime language of the cache."""
        version: str  # "3.8.12"
        """The language version of the cache."""
        image_name: str  # "Local"
        """The name of the cache's execution environment."""

    def __init__(
        self,
        ctx: Context,
        path: str,
        /,
        **attributes: Unpack[_Attrs],
    ) -> None:
        super().__init__(ctx, path, **attributes)

    class _DestroyAttrs(TypedDict, total=False):
        dry_run: bool
        """If `True`, the cache will not be destroyed, only the operation will be simulated."""

    def destroy(self, **kwargs: Unpack[SystemRuntimeCache._DestroyAttrs]) -> Task:
        """
        Remove a content runtime package cache.

        This action is only available to administrators.

        Parameters
        ----------
        dry_run : bool, optional
            If `True`, the cache will not be destroyed, only the operation will be simulated.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client()

        runtime_caches = client.system.caches.runtime.find()
        first_runtime_cache = runtime_caches[0]

        # Remove the cache
        task = first_runtime_cache.destroy(dry_run=True)

        # Wait for the task to finish
        task.wait_for()
        ```
        """
        url = self._ctx.url + self._path
        data = dict(self)
        response = self._ctx.session.delete(url, json={**data, **kwargs})

        task_id = response.json().get("task_id")
        if not task_id:
            raise RuntimeError("`task_id` not found in response.")
        task = self._ctx.client.tasks.get(task_id)
        return task


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
        from posit.connect import Client

        client = Client()

        runtime_caches = client.system.caches.runtime.find()
        ```
        """
        url = self._ctx.url + self._path
        response = self._ctx.session.get(url)
        results = response.json()
        if not isinstance(results, dict) and "caches" not in results:
            raise RuntimeError("`caches=` not found in response.")
        caches = results["caches"]
        return [SystemRuntimeCache(self._ctx, self._path, **cache) for cache in caches]

    @overload
    def destroy(self, cache: SystemRuntimeCache, /) -> Task: ...
    @overload
    def destroy(
        self,
        /,
        *,
        language: str,
        version: str,
        image_name: str,
        dry_run: bool = False,
    ) -> Task: ...

    def destroy(
        self,
        cache: Optional[SystemRuntimeCache] = None,
        /,
        **kwargs,
    ) -> Task:
        """
        Delete a content runtime package cache.

        Delete a content runtime package cache by specifying language, version, and execution
        environment.

        This action is only available to administrators.

        Parameters
        ----------
        cache : SystemRuntimeCache
            The system runtime cache object to destroy.
        language : str
            The runtime language of the cache.
        version : str
            The language version of the cache.
        image_name : str
            The name of the cache's execution environment.
        dry_run : bool, optional
            If `True`, the cache will not be destroyed, only the operation will be simulated.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client()

        runtime_caches = client.system.caches.runtime.find()
        first_runtime_cache = runtime_caches[0]

        # Remove the cache
        task = client.system.caches.runtime.destroy(first_runtime_cache, dry_run=True)

        # Or, remove the cache by specifying the cache's attributes
        task = client.system.caches.runtime.destroy(
            language="Python",
            version="3.12.5",
            image_name="Local",
            dry_run=True,
        )
        ```
        """
        if cache is None:
            cache = SystemRuntimeCache(self._ctx, self._path, **kwargs)
        else:
            if not isinstance(cache, SystemRuntimeCache):
                raise TypeError(
                    f"Expected `cache` to be of type `SystemRuntimeCache`. Received {type(cache)}"
                )

        return cache.destroy(**kwargs)
