from __future__ import annotations

from typing import Optional

from typing_extensions import TypedDict

from .._types_context import ContextP
from ..context import Context
from .integrations import Integrations
from .sessions import Sessions


class OAuth(ContextP[Context]):
    def __init__(self, ctx: Context, api_key: str) -> None:
        super().__init__()
        self._ctx = ctx

        # TODO-barret-q: Is this used?
        self.api_key = api_key

    @property
    def integrations(self):
        return Integrations(self._ctx)

    @property
    def sessions(self):
        return Sessions(self._ctx)

    def get_credentials(self, user_session_token: Optional[str] = None) -> Credentials:
        url = self._ctx.url + "v1/oauth/integrations/credentials"

        # craft a credential exchange request
        data = {}
        data["grant_type"] = "urn:ietf:params:oauth:grant-type:token-exchange"
        data["subject_token_type"] = "urn:posit:connect:user-session-token"
        if user_session_token:
            data["subject_token"] = user_session_token

        response = self._ctx.session.post(url, data=data)
        return Credentials(**response.json())


class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str
