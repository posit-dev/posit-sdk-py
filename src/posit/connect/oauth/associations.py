"""OAuth association resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from typing_extensions import TypedDict, Unpack

from .._active import ResourceDict
from .._api_call import ApiCallMixin
from .._json import Jsonifiable, JsonifiableList
from .._types_content_item import ContentItemContext
from .._types_context import ContextP
from ._types_context_integration import IntegrationContext

if TYPE_CHECKING:
    from ..context import Context


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

    def __init__(self, ctx: Context, /, **kwargs: Unpack[_Attrs]) -> None:
        super().__init__(ctx, **kwargs)


class IntegrationAssociations(ContextP[IntegrationContext]):
    """IntegrationAssociations resource."""

    def __init__(self, ctx: IntegrationContext) -> None:
        super().__init__()
        self._ctx = ctx

    def find(self) -> list[Association]:
        """Find OAuth associations.

        Returns
        -------
        list[Association]
        """
        path = f"v1/oauth/integrations/{self._ctx.integration_guid}/associations"
        url = self._ctx.url + path

        response = self._ctx.session.get(url)
        return [
            Association(
                self._ctx,
                **result,
            )
            for result in response.json()
        ]


class ContentItemAssociations(ApiCallMixin, ContextP[ContentItemContext]):
    """ContentItemAssociations resource."""

    @classmethod
    def _api_path(cls, content_guid: str) -> str:
        return f"v1/content/{content_guid}/oauth/integrations/associations"

    def __init__(self, ctx: ContentItemContext) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = self._api_path(ctx.content_guid)

    # TODO-barret-future-q: Should this be inherited from ActiveFinderSequence? (It would add find_by)
    def find(self) -> list[Association]:
        """Find OAuth associations.

        Returns
        -------
        list[Association]
        """
        results: Jsonifiable = self._get_api()
        results_list = cast(JsonifiableList, results)
        return [
            Association(
                self._ctx,
                **result,
            )
            for result in results_list
        ]

    # TODO-barret-future-q: Should this be destroy instead of delete?
    def delete(self) -> None:
        """Delete integration associations."""
        data = []
        self._put_api(json=data)

    def update(self, integration_guid: str) -> None:
        """Set integration associations."""
        data = [{"oauth_integration_guid": integration_guid}]

        self._put_api(json=data)
