from __future__ import annotations

from typing import Optional, TypedDict

from .. import resources

from .integrations import Integrations
from .sessions import Sessions

class OAuth(resources.Resources):
   
    def __init__(self, params: resources.ResourceParameters, api_key: str) -> None:
        super().__init__(params)
        self.api_key = api_key 

    @property
    def integrations(self):
        return Integrations(self.params)

    @property
    def sessions(self):
        return Sessions(self.params)

    def get_credentials(
        self, 
        user_session_token: Optional[str] = None
    ) -> Credentials:

        url = self.params.url + "v1/oauth/integrations/credentials"


        # craft a basic credential exchange request where the self.config.api_key owner
        # is requesting their own credentials
        data = dict()
        data["grant_type"] = "urn:ietf:params:oauth:grant-type:token-exchange"
        data["subject_token_type"] = "urn:posit:connect:api-key"
        data["subject_token"] = self.api_key

        # if this content is running on Connect, then it is allowed to request
        # the content viewer's credentials
        if user_session_token:
            data["subject_token_type"] = "urn:posit:connect:user-session-token"
            data["subject_token"] = user_session_token

        response = self.session.post(url, data=data)
        return Credentials(**response.json())
    
    
class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str
