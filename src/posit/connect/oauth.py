from __future__ import annotations

from requests import Session
from typing import Optional, TypedDict

from . import urls
from .config import Config


class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str


class OAuthIntegration:
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append(config.url, "v1/oauth/integrations/credentials")
        self.config = config
        self.session = session

    def get_credentials(
        self, user_session_token: Optional[str] = None
    ) -> Credentials:
        # craft a basic credential exchange request where the self.config.api_key owner
        # is requesting their own credentials
        data = dict()
        data["grant_type"] = "urn:ietf:params:oauth:grant-type:token-exchange"
        data["subject_token_type"] = "urn:posit:connect:api-key"
        data["subject_token"] = self.config.api_key

        # if this content is running on Connect, then it is allowed to request
        # the content viewer's credentials
        if user_session_token:
            data["subject_token_type"] = "urn:posit:connect:user-session-token"
            data["subject_token"] = user_session_token

        response = self.session.post(self.url, data=data)
        return Credentials(**response.json())
