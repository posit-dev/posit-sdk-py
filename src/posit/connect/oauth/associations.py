"""OAuth association resources."""

from __future__ import annotations

import re

from typing_extensions import TYPE_CHECKING, List, Optional

# from ..context import requires
from ..resources import BaseResource, Resources

if TYPE_CHECKING:
    from ..context import Context
    from ..oauth import types


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

    # TODO turn this on before merging
    # @requires("2025.07.0")
    def find_by(
        self,
        integration_type: Optional[types.OAuthIntegrationType] = None,
        auth_type: Optional[types.OAuthIntegrationAuthType] = None,
        name: Optional[str] = None,
        guid: Optional[str] = None,
    ) -> Association | None:
        for association in self.find():
            match = True

            if (
                integration_type is not None
                and association.get("oauth_integration_template") != integration_type
            ):
                match = False

            if (
                auth_type is not None
                and association.get("oauth_integration_auth_type") != auth_type
            ):
                match = False

            if name is not None:
                integration_name = association.get("oauth_integration_name", "")
                if not re.search(name, integration_name):
                    match = False

            if guid is not None and association.get("oauth_integration_guid") != guid:
                match = False

            if match:
                return association
        return None

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
