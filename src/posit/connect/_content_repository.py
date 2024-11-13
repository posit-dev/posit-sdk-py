from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    cast,
)

from ._active import ActiveDict, JsonifiableDict
from ._types_content_item import ContentItemContext
from ._typing_extensions import NotRequired, TypedDict, Unpack

if TYPE_CHECKING:
    from .context import Context


class ContentItemRepository(ActiveDict):
    """
    Content items GitHub repository information.

    See Also
    --------
    * Get info: https://docs.posit.co/connect/api/#get-/v1/content/-guid-/repository
    * Delete info: https://docs.posit.co/connect/api/#delete-/v1/content/-guid-/repository
    * Update info: https://docs.posit.co/connect/api/#patch-/v1/content/-guid-/repository
    """

    class _Attrs(TypedDict, total=False):
        repository: str
        """URL for the repository."""
        branch: NotRequired[str]
        """The tracked Git branch."""
        directory: NotRequired[str]
        """Directory containing the content."""
        polling: NotRequired[bool]
        """Indicates that the Git repository is regularly polled."""

    def __init__(
        self,
        ctx: ContentItemContext,
        /,
        # By default, the `attrs` will be retrieved from the API if no `attrs` are supplied.
        **attrs: Unpack[ContentItemRepository._Attrs],
    ) -> None:
        """Content items GitHub repository information.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        **attrs : ContentItemRepository._Attrs
            Attributes for the content item repository. If not supplied, the attributes will be
            retrieved from the API upon initialization
        """
        path = self._api_path(ctx.content_guid)
        # Only fetch data if `attrs` are not supplied
        get_data = len(attrs) == 0
        super().__init__(ctx, path, get_data, **attrs)

    @classmethod
    def _api_path(cls, content_guid: str) -> str:
        return f"v1/content/{content_guid}/repository"

    @classmethod
    def _create(
        cls,
        ctx: Context,
        content_guid: str,
        **attrs: Unpack[ContentItemRepository._Attrs],
    ) -> ContentItemRepository:
        from ._api_call import put_api

        result = put_api(ctx, cls._api_path(content_guid), json=cast(JsonifiableDict, attrs))
        content_ctx = (
            ctx
            if isinstance(ctx, ContentItemContext)
            else ContentItemContext(ctx, content_guid=content_guid)
        )

        return ContentItemRepository(
            content_ctx,
            **result,  # pyright: ignore[reportCallIssue]
        )

    def destroy(self) -> None:
        """
        Delete the content's git repository location.

        See Also
        --------
        * https://docs.posit.co/connect/api/#delete-/v1/content/-guid-/repository
        """
        self._delete_api()

    def update(
        self,
        # *,
        **attrs: Unpack[ContentItemRepository._Attrs],
    ) -> ContentItemRepository:
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
        result = self._patch_api(json=cast(JsonifiableDict, dict(attrs)))
        return ContentItemRepository(
            self._ctx,
            **result,  # pyright: ignore[reportCallIssue]
        )
