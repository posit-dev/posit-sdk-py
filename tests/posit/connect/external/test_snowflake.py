from unittest.mock import patch

import responses

from posit.connect import Client
from posit.connect.external.snowflake import PositAuthenticator


def register_mocks():
    responses.post(
        "https://connect.example/__api__/v1/oauth/integrations/credentials",
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                    "subject_token_type": "urn:posit:connect:user-session-token",
                    "subject_token": "cit",
                },
            ),
        ],
        json={
            "access_token": "dynamic-viewer-access-token",
            "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "token_type": "Bearer",
        },
    )


class TestPositAuthenticator:
    @responses.activate
    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_posit_authenticator(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        auth = PositAuthenticator(
            local_authenticator="SNOWFLAKE",
            user_session_token="cit",
            client=client,
        )
        assert auth.authenticator == "oauth"
        assert auth.token == "dynamic-viewer-access-token"

    def test_posit_authenticator_fallback(self):
        # local_authenticator is used when the content is running locally
        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        auth = PositAuthenticator(
            local_authenticator="SNOWFLAKE",
            user_session_token="cit",
            client=client,
        )
        assert auth.authenticator == "SNOWFLAKE"
        assert auth.token is None
