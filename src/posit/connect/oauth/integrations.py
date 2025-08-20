"""OAuth integration resources."""

from __future__ import annotations

from functools import partial

from typing_extensions import TYPE_CHECKING, List, Optional, overload

from ..resources import (
    BaseResource,
    Resources,
    _contains_dict_key_values,
    _matches_exact,
    _matches_pattern,
)
from .associations import IntegrationAssociations

if TYPE_CHECKING:
    from ..oauth import types


class Integration(BaseResource):
    """OAuth integration resource."""

    @property
    def associations(self) -> IntegrationAssociations:
        return IntegrationAssociations(self._ctx, integration_guid=self["guid"])

    def delete(self) -> None:
        """Delete the OAuth integration."""
        path = f"v1/oauth/integrations/{self['guid']}"
        self._ctx.client.delete(path)

    @overload
    def update(
        self,
        *args,
        name: str = ...,
        description: str = ...,
        config: dict = ...,
        **kwargs,
    ) -> None:
        """Update the OAuth integration.

        Parameters
        ----------
        name: str, optional
        description: str, optional
        config: dict, optional
        """

    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the OAuth integration."""

    def update(self, *args, **kwargs) -> None:
        """Update the OAuth integration."""
        body = dict(*args, **kwargs)
        path = f"v1/oauth/integrations/{self['guid']}"
        response = self._ctx.client.patch(path, json=body)
        super().update(**response.json())


class Integrations(Resources):
    """Integrations resource."""

    @overload
    def create(
        self,
        *,
        name: str,
        description: Optional[str],
        template: str,
        config: dict,
    ) -> Integration:
        """Create an OAuth integration.

        Parameters
        ----------
        name : str
        description : Optional[str]
        template : str
        config : dict

        Returns
        -------
        Integration
        """

    @overload
    def create(self, **kwargs) -> Integration:
        """Create an OAuth integration.

        Returns
        -------
        Integration
        """

    def create(self, **kwargs) -> Integration:
        """Create an OAuth integration.

        Parameters
        ----------
        name : str
        description : Optional[str]
        template : str
        config : dict

        Returns
        -------
        Integration
        """
        path = "v1/oauth/integrations"
        response = self._ctx.client.post(path, json=kwargs)
        return Integration(self._ctx, **response.json())

    def find(self) -> List[Integration]:
        """Find OAuth integrations.

        Returns
        -------
        List[Integration]
        """
        path = "v1/oauth/integrations"
        response = self._ctx.client.get(path)
        return [
            Integration(
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
        config: Optional[dict] = None,
    ) -> Integration | None:
        """Find an OAuth integration by various criteria.

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
        config : Optional[dict]
            A dictionary of configuration key-value pairs to match against the integration's config. This will
            vary based on the integration type.

        Returns
        -------
        Integration | None
            The first matching integration, or None if no match is found.
        """
        filters = []
        if integration_type is not None:
            filters.append(partial(_matches_exact, key="template", value=integration_type))
        if auth_type is not None:
            filters.append(partial(_matches_exact, key="auth_type", value=auth_type))
        if name is not None:
            filters.append(partial(_matches_pattern, key="name", pattern=name))
        if description is not None:
            filters.append(partial(_matches_pattern, key="description", pattern=description))
        if guid is not None:
            filters.append(partial(_matches_exact, key="guid", value=guid))
        if config is not None:
            filters.append(partial(_contains_dict_key_values, key="config", value=config))

        for integration in self.find():
            if all(f(integration) for f in filters):
                return integration

        return None

    def get(self, guid: str) -> Integration:
        """Get an OAuth integration.

        Parameters
        ----------
        guid: str

        Returns
        -------
        Integration
        """
        path = f"v1/oauth/integrations/{guid}"
        response = self._ctx.client.get(path)
        return Integration(self._ctx, **response.json())
