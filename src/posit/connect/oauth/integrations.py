from ..resources import Resource, Resources 
from typing import Optional, overload, List

class Integration(Resource):
    """OAuth integration resource.
    
    Attributes
    ----------
    id : str
        The internal numeric identifier of this OAuth integration.
    guid : str
        The unique identifier of this OAuth integration which is used in REST API requests.
    name : str
        A descriptive name to identify each OAuth integration.
    description : Optional[str]
        A brief text to describe each OAuth integration
    template : str
        The template to use to configure this OAuth integration.
    config : dict
        The OAuth integration configuration based on the template.
    created_time : str
        The timestamp (RFC3339) indicating when this OAuth integration was created.
    updated_time : str
        The timestamp (RFC3339) indicating when this OAuth integration was last updated.
    """

   
    # CRUD Methods
    
    def delete(self) -> None:
        """Delete the OAuth integration."""
        path = f"v1/oauth/integrations/{self.guid}"
        url = self.url + path
        self.session.delete(url)
        
    
    @overload
    def update(self,
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
        ...


    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the OAuth integration."""
        ...


    def update(self, *args, **kwargs) -> None:
        """Update the OAuth integration."""
        body = dict(*args, **kwargs)
        url = self.url + f"v1/oauth/integrations/{self.guid}"
        response = self.session.patch(url, json=body)
        super().update(**response.json())
        ...
        
    # Properties
    
    @property
    def id(self) -> str:
        return self.get("id")  # type: ignore

    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def name(self) -> str:
        return self.get("name")  # type: ignore
    
    @property
    def description(self) -> Optional[str]:
        return self.get("description") # type: ignore
    
    @property
    def template(self) -> str:
        return self.get("template") # type: ignore
    
    @property
    def config(self) -> dict:
        return self.get("config") # type: ignore
    
    @property
    def created_time(self) -> str:
        return self.get("created_time") # type: ignore
    
    @property
    def updated_time(self) -> str:
        return self.get("updated_time") # type: ignore
    
class Integrations(Resources):
    """Integrations resource.
    """

    @overload
    def create(self,
               *,
               name: str,
               description: Optional[str],
               template: str,
               config: dict) -> Integration:
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
        ...

    @overload
    def create(self, **kwargs) -> Integration:
        """Create an OAuth integration.

        Returns
        -------
        Integration
        """
        ...

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
        ...
        path = "v1/oauth/integrations"
        url = self.url + path
        response = self.session.post(url, json=kwargs)
        return Integration(self.params, **response.json())

       
    def find(self) -> List[Integration]:
        """Find OAuth integrations.
        Returns
        -------
        List[Integration]
        """
        path = "v1/oauth/integrations"
        url = self.url + path
        
        response = self.session.get(url)
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
        url = self.url + path
        response = self.session.get(url)
        return Integration(self.params, **response.json())
