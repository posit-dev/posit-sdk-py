"""OAuth integration resources."""

from typing_extensions import List, Optional, overload

from ..resources import BaseResource, Resources
from .associations import IntegrationAssociations


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
