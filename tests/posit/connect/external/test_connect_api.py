from unittest.mock import patch

import responses

from posit.connect import Client
from posit.connect.external.connect_api import ConnectAPIKeyProvider


def register_mocks():
    responses.post(
        "https://connect.example/__api__/v1/oauth/integrations/credentials",
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                    "subject_token_type": "urn:posit:connect:user-session-token",
                    "subject_token": "cit",
                    "requested_token_type": "urn:posit:connect:api-key",
                },
            ),
        ],
        json={
            "access_token": "viewer-api-key",
            "issued_token_type": "urn:posit:connect:api-key",
            "token_type": "Key",
        },
    )


class TestConnectAPIKeyProvider:
    @responses.activate
    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_provider(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        auth = ConnectAPIKeyProvider(
            client=client,
            user_session_token="cit",
        )
        assert auth.viewer == "viewer-api-key"

    def test_provider_fallback(self):
        # local_authenticator is used when the content is running locally
        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        auth = ConnectAPIKeyProvider(
            client=client,
            user_session_token="cit",
        )
        assert auth.viewer is None
