"""OAuth association resources."""

from typing import List 

from ..resources import Resource, ResourceParameters, Resources


class Association(Resource):
    pass


class IntegrationAssociations(Resources):
    """IntegrationAssociations resource."""

    def __init__(self, params: ResourceParameters, integration_guid: str) -> None:
        super().__init__(params)
        self.integration_guid = integration_guid 

    def find(self) -> List[Association]:
        """Find OAuth associations.

        Returns
        -------
        List[Association]
        """
        path = f"v1/oauth/integrations/{self.integration_guid}/associations"
        url = self.params.url + path

        response = self.params.session.get(url)
        return [
            Association(
                self.params,
                **result,
            )
            for result in response.json()
        ]


class ContentItemAssociations(Resources):
    """ContentItemAssociations resource."""

    def __init__(self, params: ResourceParameters, content_guid: str) -> None:
        super().__init__(params) 
        self.content_guid = content_guid


    def find(self) -> List[Association]:
        """Find OAuth associations.

        Returns
        -------
        List[Association]
        """
        path = f"v1/content/{self.content_guid}/oauth/integrations/associations"
        url = self.params.url + path
        response = self.params.session.get(url)
        return [
            Association(
                self.params,
                **result,
            )
            for result in response.json()
        ]


    def update(self, integration_guid: None | str) -> None:
        """Set integration associations"""
       

        if integration_guid is None:
            data = []
        else:
            data = [{"oauth_integration_guid": integration_guid}]

        path = f"v1/content/{self.content_guid}/oauth/integrations/associations"
        url = self.params.url + path
        self.params.session.put(url, json=data)
