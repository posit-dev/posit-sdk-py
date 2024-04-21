from __future__ import annotations

from requests import Session
from typing import Optional, TypedDict

from . import context, urls


class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str


class OAuthIntegration:
    def __init__(self, ctx: context.Context) -> None:
        self.ctx = ctx
        self.url = urls.append(ctx.url, "v1/oauth/integrations/credentials")

    def get_credentials(
        self, user_session_token: Optional[str] = None
    ) -> Credentials:
        # craft a basic credential exchange request where the self.config.api_key owner
        # is requesting their own credentials
        data = dict()
        data["grant_type"] = "urn:ietf:params:oauth:grant-type:token-exchange"
        data["subject_token_type"] = "urn:posit:connect:api-key"
        data["subject_token"] = self.ctx.api_key

        # if this content is running on Connect, then it is allowed to request
        # the content viewer's credentials
        if user_session_token:
            data["subject_token_type"] = "urn:posit:connect:user-session-token"
            data["subject_token"] = user_session_token

        response = self.ctx.session.post(self.url, data=data)
        return Credentials(**response.json())
