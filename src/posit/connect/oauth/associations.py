"""OAuth association resources."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import List

from ..resources import BaseResource, Resources

if TYPE_CHECKING:
    from ..context import Context


class Association(BaseResource):
    pass


class IntegrationAssociations(Resources):
    """IntegrationAssociations resource."""

    def __init__(self, ctx: Context, integration_guid: str) -> None:
        super().__init__(ctx)
        self.integration_guid = integration_guid

    def find(self) -> List[Association]:
        """Find OAuth associations.

        Returns
        -------
        List[Association]
        """
        path = f"v1/oauth/integrations/{self.integration_guid}/associations"
        response = self._ctx.client.get(path)
        return [
            Association(
                self._ctx,
                **result,
            )
            for result in response.json()
        ]


class ContentItemAssociations(Resources):
    """ContentItemAssociations resource."""

    def __init__(self, ctx, content_guid: str):
        super().__init__(ctx)
        self.content_guid = content_guid

    def find(self) -> List[Association]:
        """Find OAuth associations.

        Returns
        -------
        List[Association]
        """
        path = f"v1/content/{self.content_guid}/oauth/integrations/associations"
        response = self._ctx.client.get(path)
        return [
            Association(
                self._ctx,
                **result,
            )
            for result in response.json()
        ]

    def delete(self) -> None:
        """Delete integration associations."""
        data = []

        path = f"v1/content/{self.content_guid}/oauth/integrations/associations"
        self._ctx.client.put(path, json=data)

    def update(self, integration_guid: str | list[str]) -> None:
        """Set integration associations."""
        if isinstance(integration_guid, str):
            integration_guid = [integration_guid]
        data = [{"oauth_integration_guid": guid} for guid in integration_guid]

        path = f"v1/content/{self.content_guid}/oauth/integrations/associations"
        self._ctx.client.put(path, json=data)
