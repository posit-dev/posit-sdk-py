from __future__ import annotations

import base64
import os
import json
from typing import Optional, TYPE_CHECKING

from requests import Response

if TYPE_CHECKING:
    from .client import Client

# https://github.com/jpadilla/pyjwt/blob/12420204cfef8fea7644532b9ca82c0cc5ca3abe/jwt/utils.py#L25-L33
# https://github.com/golang-jwt/jwt/blob/80dccb9209ebe7b503c067dc830fcbd4aa2e74eb/MIGRATION_GUIDE.md?plain=1#L34-L38
# parse_target_guid fixes the jwt payload padding before base64 decoding the payload and parsing the json.
# The sub claim containing the target user guid is returned.
def parse_target_guid(content_identity: str) -> str:
    payload = content_identity.split(".")[1].encode("utf-8")
    rem = len(payload) % 4
    if rem > 0:
        payload += b"=" * (4 - rem)
    payload = base64.urlsafe_b64decode(payload)
    return json.loads(payload)['sub']


class OAuthIntegration:
    def __init__(
            self, client: Client, *args
    ) -> None:
        super().__init__()
        self.client = client

    def get_credentials(self, content_identity: Optional[str]) -> Response:
        endpoint = os.path.join(self.client._config.endpoint, "v1/oauth/integrations/credentials")

        # craft a basic credential exchange request where the self.config.api_key owner
        # is requesting their own credentials
        data = dict()
        data["grant_type"] = "urn:ietf:params:oauth:grant-type:token-exchange"
        data["subject_token_type"] = "urn:posit:connect:user-guid"
        data["subject_token"] = self.client.me.get('guid')

        # if this content is running on Connect, then it is allowed to request
        # the content viewer's credentials
        if content_identity:
            data["subject_token"] = parse_target_guid(content_identity)
            data["actor_token_type"] = "urn:posit:connect:content-identity-token"
            data["actor_token"] = content_identity

        return self.client._session.post(endpoint, data=data)


