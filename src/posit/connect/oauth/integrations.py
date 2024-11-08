"""OAuth integration resources."""

from typing import List, Optional, overload

from ..resources import Resource, Resources
from .associations import IntegrationAssociations


class Integration(Resource):
    """OAuth integration resource."""

    @property
    def associations(self) -> IntegrationAssociations:
        return IntegrationAssociations(self.params, integration_guid=self["guid"])

    def delete(self) -> None:
        """Delete the OAuth integration."""
        path = f"v1/oauth/integrations/{self['guid']}"
        url = self.params.url + path
        self.params.session.delete(url)

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
        url = self.params.url + f"v1/oauth/integrations/{self['guid']}"
        response = self.params.session.patch(url, json=body)
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
        url = self.params.url + path
        response = self.params.session.post(url, json=kwargs)
        return Integration(self.params, **response.json())

    def find(self) -> List[Integration]:
        """Find OAuth integrations.

        Returns
        -------
        List[Integration]
        """
        path = "v1/oauth/integrations"
        url = self.params.url + path

        response = self.params.session.get(url)
        return [
            Integration(
                self.params,
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
        url = self.params.url + path
        response = self.params.session.get(url)
        return Integration(self.params, **response.json())
