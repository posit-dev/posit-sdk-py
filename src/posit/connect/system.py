"""System resources."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, List, Literal, TypedDict, Unpack, overload

from .context import ContextManager
from .resources import Active

if TYPE_CHECKING:
    from .context import Context
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

    @overload
    def destroy(self, *, dry_run: Literal[True]) -> None: ...
    @overload
    def destroy(self, *, dry_run: Literal[False] = False) -> Task: ...
    def destroy(self, **kwargs) -> Task | None:
        """
        Remove a content runtime package cache.

        This action is only available to administrators.

        Parameters
        ----------
        dry_run : bool, optional
            If `True`, the cache will not be destroyed, only the operation will be simulated.

        Returns
        -------
        Task | None
            The task object if the operation was successful. If `dry_run=True`, `None` is returned.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client()

        runtime_caches = client.system.caches.runtime.find()
        first_runtime_cache = runtime_caches[0]

        # Remove the cache
        task = first_runtime_cache.destroy(dry_run=False)

        # Wait for the task to finish
        task.wait_for()
        ```
        """
        body = {**self, **kwargs}
        response = self._ctx.client.delete(self._path, json=body)

        task_id = response.json().get("task_id")
        if not task_id:
            return None
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
        response = self._ctx.client.get(self._path)
        results = response.json()
        return [SystemRuntimeCache(self._ctx, self._path, **cache) for cache in results["caches"]]

    @overload
    def destroy(
        self,
        /,
        *,
        language: str,
        version: str,
        image_name: str,
        dry_run: Literal[False] = False,
    ) -> Task: ...
    @overload
    def destroy(
        self,
        /,
        *,
        language: str,
        version: str,
        image_name: str,
        dry_run: Literal[True] = True,
    ) -> None: ...

    def destroy(
        self,
        /,
        **kwargs,
    ) -> Task | None:
        """
        Delete a content runtime package cache.

        Delete a content runtime package cache by specifying language, version, and execution
        environment.

        This action is only available to administrators.

        Parameters
        ----------
        language : str
            The runtime language of the cache.
        version : str
            The language version of the cache.
        image_name : str
            The name of the cache's execution environment.
        dry_run : bool, optional
            If `True`, the cache will not be destroyed, only the operation will be simulated.

        Returns
        -------
        Task | None
            The task object if the operation was successful. If `dry_run=True`, `None` is returned.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client()

        runtime_caches = client.system.caches.runtime.find()
        first_runtime_cache = runtime_caches[0]

        # Remove the cache
        task = first_runtime_cache.destroy(dry_run=False)

        # Or, remove the cache by specifying the cache's attributes
        task = client.system.caches.runtime.destroy(
            language="Python",
            version="3.12.5",
            image_name="Local",
            dry_run=False,
        )
        ```
        """
        dry_run: bool | None = kwargs.pop("dry_run", None)
        runtime_cache = SystemRuntimeCache(self._ctx, self._path, **kwargs)

        # Only add `dry_run=` argument if it is provided by user
        dry_run_args = {}
        if dry_run is not None:
            dry_run_args["dry_run"] = dry_run
        return runtime_cache.destroy(**dry_run_args)
