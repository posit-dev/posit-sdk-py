"""Content item repository."""

from __future__ import annotations

from typing_extensions import (
    Optional,
    Protocol,
    overload,
    runtime_checkable,
)

from .errors import ClientError
from .resources import Resource, _Resource


# ContentItem Repository uses a PATCH method, not a PUT for updating.
class _ContentItemRepository(_Resource):
    def update(self, **attributes):
        response = self._ctx.client.patch(self._path, json=attributes)
        result = response.json()
        # # Calling this method will call `_Resource.update` which will try to PUT to the path.
        # super().update(**result)
        # Instead, update the dict directly.
        dict.update(self, **result)


@runtime_checkable
class ContentItemRepository(Resource, Protocol):
    """
    Content items GitHub repository information.

    See Also
    --------
    * Get info: https://docs.posit.co/connect/api/#get-/v1/content/-guid-/repository
    * Delete info: https://docs.posit.co/connect/api/#delete-/v1/content/-guid-/repository
    * Update info: https://docs.posit.co/connect/api/#patch-/v1/content/-guid-/repository
    """

    def destroy(self) -> None:
        """
        Delete the content's git repository location.

        See Also
        --------
        * https://docs.posit.co/connect/api/#delete-/v1/content/-guid-/repository
        """
        ...

    def update(
        self,
        *,
        repository: Optional[str] = None,
        branch: str = "main",
        directory: str = ".",
        polling: bool = False,
    ) -> None:
        """Update the content's repository.

        Parameters
        ----------
        repository: str, optional
            URL for the repository. Default is None.
        branch: str, optional
            The tracked Git branch. Default is 'main'.
        directory: str, optional
            Directory containing the content. Default is '.'
        polling: bool, optional
            Indicates that the Git repository is regularly polled. Default is False.

        Returns
        -------
        None

        See Also
        --------
        * https://docs.posit.co/connect/api/#patch-/v1/content/-guid-/repository
        """
        ...


class ContentItemRepositoryMixin(Resource):
    @property
    def repository(self) -> ContentItemRepository | None:
        try:
            path = f"v1/content/{self['guid']}/repository"
            response = self._ctx.client.get(path)
            result = response.json()
            return _ContentItemRepository(
                self._ctx,
                path,
                **result,
            )
        except ClientError:
            return None

    @overload
    def create_repository(
        self,
        /,
        *,
        repository: Optional[str] = None,
        branch: str = "main",
        directory: str = ".",
        polling: bool = False,
    ) -> ContentItemRepository: ...

    @overload
    def create_repository(self, /, **attributes) -> ContentItemRepository: ...

    def create_repository(self, /, **attributes) -> ContentItemRepository:
        """Create repository.

        Parameters
        ----------
        repository : str
            URL for the respository.
        branch : str, optional
            The tracked Git branch. Default is 'main'.
        directory : str, optional
            Directory containing the content. Default is '.'.
        polling : bool, optional
            Indicates that the Git repository is regularly polled. Default is False.

        Returns
        -------
        ContentItemRepository
        """
        path = f"v1/content/{self['guid']}/repository"
        response = self._ctx.client.put(path, json=attributes)
        result = response.json()

        return _ContentItemRepository(
            self._ctx,
            path,
            **result,
        )
