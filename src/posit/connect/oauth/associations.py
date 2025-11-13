"""OAuth association resources."""

from __future__ import annotations

from functools import partial

from typing_extensions import TYPE_CHECKING, List, Optional, overload

from ..resources import BaseResource, Resources, _matches_exact, _matches_pattern

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

    def find_by(
        self,
        integration_type: Optional[types.OAuthIntegrationType | str] = None,
        auth_type: Optional[types.OAuthIntegrationAuthType | str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        guid: Optional[str] = None,
    ) -> Association | None:
        """Find an OAuth integration associated with content by various criteria.

        Parameters
        ----------
        integration_type : Optional[types.OAuthIntegrationType | str]
            The type of the integration (e.g., "aws", "azure").
        auth_type : Optional[types.OAuthIntegrationAuthType | str]
            The authentication type of the integration (e.g., "Viewer", "Service Account").
        name : Optional[str]
            A regex pattern to match the integration name. For exact matches, use `^` and `$`. For example,
            `^My Integration$` will match only "My Integration".
        description : Optional[str]
            A regex pattern to match the integration description. For exact matches, use `^` and `$`. For example,
            `^My Integration Description$` will match only "My Integration Description".
        guid : Optional[str]
            The unique identifier of the integration.

        Returns
        -------
        Association | None
            The first matching association, or None if no match is found.
        """
        filters = []
        if integration_type is not None:
            filters.append(
                partial(_matches_exact, key="oauth_integration_template", value=integration_type)
            )
        if auth_type is not None:
            filters.append(
                partial(_matches_exact, key="oauth_integration_auth_type", value=auth_type)
            )
        if name is not None:
            filters.append(partial(_matches_pattern, key="oauth_integration_name", pattern=name))
        if description is not None:
            filters.append(
                partial(_matches_pattern, key="oauth_integration_description", pattern=description)
            )
        if guid is not None:
            filters.append(partial(_matches_exact, key="oauth_integration_guid", value=guid))

        for association in self.find():
            if all(f(association) for f in filters):
                return association

        return None

    def delete(self) -> None:
        """Delete integration associations."""
        data = []

        path = f"v1/content/{self.content_guid}/oauth/integrations/associations"
        self._ctx.client.put(path, json=data)

    @overload
    def update(self, integration_guid: str) -> None:
        """Set a single integration association.

        Parameters
        ----------
        integration_guid : str
            The unique identifier of the integration.
        """

    @overload
    def update(self, integration_guid: list[str]) -> None:
        """Set multiple integration associations.

        Parameters
        ----------
        integration_guids : list[str]
            A list of unique identifiers of the integrations.
        """

    def update(self, integration_guid: str | list[str]) -> None:
        """Set integration associations."""
        if isinstance(integration_guid, str):
            integration_guids = [integration_guid]
        else:
            integration_guids = integration_guid

        data = [{"oauth_integration_guid": guid} for guid in integration_guids]

        path = f"v1/content/{self.content_guid}/oauth/integrations/associations"
        self._ctx.client.put(path, json=data)
